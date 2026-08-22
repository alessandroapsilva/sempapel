#!/usr/bin/env bash
set -Eeuo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute como root: sudo $0 [ref-git]"
  exit 1
fi

REPO_URL="https://github.com/alessandroapsilva/sempapel.git"
REF="${1:-release/11.5-enfas}"
BASE="/home/enfas"
JBOSS_HOME="$BASE/jboss-eap-7.2"
DEPLOY="$JBOSS_HOME/standalone/deployments"
SERVICE="jboss-eap"
STAMP="$(date +%Y%m%d-%H%M%S)"
BUILD="$BASE/builds/sigaex-producao-$STAMP"
BACKUP="$BASE/backups/producao-$STAMP"
WAR="$DEPLOY/sigaex.war"
HEALTH_URL="${ENFAS_HEALTH_URL:-https://treinamento.enfassempapel.enfas.com.br/sigaex/}"

mkdir -p "$BASE/builds" "$BACKUP"

command -v git >/dev/null
command -v mvn >/dev/null
command -v mysqldump >/dev/null
command -v gzip >/dev/null
systemctl cat "$SERVICE" >/dev/null
test -d "$DEPLOY"
test -f "$WAR"

AVAILABLE_KB="$(df -Pk "$BASE" | awk 'NR==2 {print $4}')"
if [ "$AVAILABLE_KB" -lt 5242880 ]; then
  echo "ERRO: menos de 5 GiB livres em $BASE"
  exit 1
fi

echo "1/8 - Backup completo do MySQL"
mysqldump \
  -u root -p \
  --all-databases \
  --single-transaction \
  --quick \
  --routines \
  --triggers \
  --events \
  --hex-blob \
  --no-tablespaces \
  --add-drop-database \
  --default-character-set=utf8mb4 \
  | gzip -9 > "$BACKUP/mysql-todos-os-bancos.sql.gz"

gzip -t "$BACKUP/mysql-todos-os-bancos.sql.gz"
sha256sum "$BACKUP/mysql-todos-os-bancos.sql.gz" \
  > "$BACKUP/mysql-todos-os-bancos.sql.gz.sha256"

echo "2/8 - Clone limpo"
git clone --branch "$REF" --single-branch "$REPO_URL" "$BUILD"
cd "$BUILD"
COMMIT="$(git rev-parse HEAD)"
git status --porcelain | grep -q . && {
  echo "ERRO: clone iniciou com alterações locais"
  exit 1
}
git show -s --format='Commit: %H%nDescrição: %s'

echo "3/8 - Validações de produção"
test ! -e "$BUILD/q"
test ! -e "$BUILD/.github/workflows/adapt-pbdoc-edita.yml"
test ! -e "$BUILD/.github/workflows/remove-anexar-final.yml"
grep -q 'A ENFAS utiliza uma numeração aleatória' \
  siga-ex/src/main/java/br/gov/jfrj/siga/ex/bl/ExBL.java
grep -q 'SecureRandom' \
  sigaex/src/main/java/br/gov/jfrj/siga/ex/service/impl/ExServiceImpl.java

echo "4/8 - Build limpo"
mvn -pl sigaex -am -DskipTests clean package

NEW_WAR="$BUILD/sigaex/target/sigaex.war"
test -s "$NEW_WAR"

echo "5/8 - Backup do WAR em execução"
cp -a "$WAR" "$BACKUP/sigaex.war.antes"
sha256sum "$WAR" > "$BACKUP/sigaex.war.antes.sha256"
sha256sum "$NEW_WAR" > "$BACKUP/sigaex.war.novo.sha256"
printf '%s\n' "$COMMIT" > "$BACKUP/commit-implantado.txt"

rollback() {
  echo "Executando rollback do SIGA-DOC"
  systemctl stop "$SERVICE" || true
  install -o enfas -g enfas -m 0644 "$BACKUP/sigaex.war.antes" "$WAR"
  for marker in deployed failed undeployed dodeploy; do
    if [ -e "$DEPLOY/sigaex.war.$marker" ]; then
      mv "$DEPLOY/sigaex.war.$marker" \
        "$BACKUP/rollback-sigaex.war.$marker-$(date +%s)"
    fi
  done
  touch "$DEPLOY/sigaex.war.dodeploy"
  chown enfas:enfas "$DEPLOY/sigaex.war.dodeploy"
  systemctl start "$SERVICE"
}

echo "6/8 - Instalação controlada"
systemctl stop "$SERVICE"

for marker in deployed failed undeployed dodeploy; do
  if [ -e "$DEPLOY/sigaex.war.$marker" ]; then
    mv "$DEPLOY/sigaex.war.$marker" "$BACKUP/sigaex.war.$marker"
  fi
done

install -o enfas -g enfas -m 0644 "$NEW_WAR" "$WAR"
touch "$DEPLOY/sigaex.war.dodeploy"
chown enfas:enfas "$DEPLOY/sigaex.war.dodeploy"

echo "7/8 - Inicialização e confirmação"
if ! systemctl start "$SERVICE"; then
  rollback
  exit 1
fi

DEPLOYED=0
for _ in $(seq 1 72); do
  if [ -f "$DEPLOY/sigaex.war.failed" ]; then
    cat "$DEPLOY/sigaex.war.failed"
    tail -n 200 "$JBOSS_HOME/standalone/log/server.log"
    rollback
    exit 1
  fi
  if [ -f "$DEPLOY/sigaex.war.deployed" ]; then
    DEPLOYED=1
    break
  fi
  sleep 5
done

if [ "$DEPLOYED" -ne 1 ]; then
  tail -n 200 "$JBOSS_HOME/standalone/log/server.log"
  rollback
  exit 1
fi

echo "8/8 - Verificação HTTP"
curl --fail --location --silent --show-error \
  --max-time 30 --output /dev/null "$HEALTH_URL"

echo "PRODUÇÃO IMPLANTADA COM SUCESSO"
echo "Commit: $COMMIT"
echo "Backup: $BACKUP"
echo "WAR: $WAR"
