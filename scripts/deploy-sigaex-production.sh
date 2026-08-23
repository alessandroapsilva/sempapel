#!/usr/bin/env bash
set -Eeuo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute como root: sudo $0 [ref-git]"
  exit 1
fi

REPO_URL="https://github.com/alessandroapsilva/sempapel.git"
REF="${1:-release/11.5.cem}"
EXPECTED_VERSION="v11.5.cem"
BASE="/home/enfas"
JBOSS_HOME="$BASE/jboss-eap-7.2"
DEPLOY="$JBOSS_HOME/standalone/deployments"
SERVICE="jboss-eap"
STAMP="$(date +%Y%m%d-%H%M%S)"
BUILD="$BASE/builds/sigaex-producao-$STAMP"
BACKUP="$BASE/backups/producao-$STAMP"
WAR="$DEPLOY/sigaex.war"
HEALTH_URL="${ENFAS_HEALTH_URL:-}"

if [ -z "$HEALTH_URL" ]; then
  echo "ERRO: defina ENFAS_HEALTH_URL com a URL real de produção."
  echo "Ex.: sudo ENFAS_HEALTH_URL=https://sempapel.enfas.com.br/sigaex/ $0 $REF"
  exit 1
fi

mkdir -p "$BASE/builds" "$BACKUP"

for cmd in git mvn mysqldump gzip curl unzip tar sha256sum; do
  command -v "$cmd" >/dev/null || { echo "ERRO: comando ausente: $cmd"; exit 1; }
done
systemctl cat "$SERVICE" >/dev/null
test -d "$DEPLOY"

AVAILABLE_KB="$(df -Pk "$BASE" | awk 'NR==2 {print $4}')"
if [ "$AVAILABLE_KB" -lt 5242880 ]; then
  echo "ERRO: menos de 5 GiB livres em $BASE"
  exit 1
fi

echo "1/8 - Backup completo do MySQL"
mysqldump -u root -p --all-databases --single-transaction --quick --routines --triggers --events --hex-blob --no-tablespaces --add-drop-database --default-character-set=utf8mb4 | gzip -9 > "$BACKUP/mysql-todos-os-bancos.sql.gz"
gzip -t "$BACKUP/mysql-todos-os-bancos.sql.gz"
sha256sum "$BACKUP/mysql-todos-os-bancos.sql.gz" > "$BACKUP/mysql-todos-os-bancos.sql.gz.sha256"

echo "2/8 - Clone limpo da release CEM"
git clone --branch "$REF" --single-branch "$REPO_URL" "$BUILD"
cd "$BUILD"
COMMIT="$(git rev-parse HEAD)"
git status --porcelain | grep -q . && { echo "ERRO: clone iniciou com alterações locais"; exit 1; }
git show -s --format='Commit: %H%nDescrição: %s'

echo "3/8 - Validações de produção"
test "$(tr -d '\r\n' < VERSION)" = "$EXPECTED_VERSION"
grep -qx -- '-Dpatch.version=cem' .mvn/maven.config
test ! -e "$BUILD/q"
test ! -e "$BUILD/.github/workflows/adapt-pbdoc-edita.yml"
test ! -e "$BUILD/.github/workflows/remove-anexar-final.yml"
grep -q 'A ENFAS utiliza uma numeração aleatória' siga-ex/src/main/java/br/gov/jfrj/siga/ex/bl/ExBL.java
grep -q 'SecureRandom' sigaex/src/main/java/br/gov/jfrj/siga/ex/service/impl/ExServiceImpl.java
for jsp in enfasOficio.jsp enfasMemorando.jsp enfasDespacho.jsp enfasInformacao.jsp enfasParecer.jsp enfasContrato.jsp enfasFolhaInicial.jsp enfasProcessoAdministrativo.jsp; do
  test -s "sigaex/src/main/webapp/paginas/expediente/modelos/$jsp"
done
test -s siga-ex/src/main/resources/db/mysql/sigaex/V123.0__ativa_modelos_jsp_institucionais_enfas.sql

echo "4/8 - Build limpo $EXPECTED_VERSION"
mvn -pl sigaex -am -DskipTests clean package
NEW_WAR="$BUILD/sigaex/target/sigaex.war"
test -s "$NEW_WAR"
unzip -p "$NEW_WAR" META-INF/MANIFEST.MF > "$BACKUP/manifest-novo.txt"
grep -q '^Patch-Version: cem' "$BACKUP/manifest-novo.txt"
grep -q '^Build-Label: v11.5.cem-' "$BACKUP/manifest-novo.txt"
sha256sum "$NEW_WAR" > "$BACKUP/sigaex.war.novo.sha256"

echo "5/8 - Backup do deployment atual"
CURRENT_KIND="none"
if [ -f "$WAR" ]; then
  CURRENT_KIND="file"
  cp -a "$WAR" "$BACKUP/sigaex.war.antes"
  sha256sum "$WAR" > "$BACKUP/sigaex.war.antes.sha256"
elif [ -d "$WAR" ]; then
  CURRENT_KIND="dir"
  tar -C "$DEPLOY" -czf "$BACKUP/sigaex.war.explodido.antes.tar.gz" sigaex.war
  sha256sum "$BACKUP/sigaex.war.explodido.antes.tar.gz" > "$BACKUP/sigaex.war.explodido.antes.tar.gz.sha256"
fi
printf '%s\n' "$CURRENT_KIND" > "$BACKUP/deployment-anterior.tipo"
printf '%s\n' "$COMMIT" > "$BACKUP/commit-implantado.txt"
printf '%s\n' "$EXPECTED_VERSION" > "$BACKUP/versao-implantada.txt"

cleanup_markers() {
  for marker in deployed failed undeployed dodeploy isdeploying pending skipdeploy; do
    rm -f "$DEPLOY/sigaex.war.$marker"
  done
}

rollback() {
  echo "Executando rollback do SIGA-DOC"
  systemctl stop "$SERVICE" || true
  cleanup_markers
  rm -rf "$WAR"
  case "$CURRENT_KIND" in
    file)
      install -o enfas -g enfas -m 0644 "$BACKUP/sigaex.war.antes" "$WAR"
      ;;
    dir)
      tar -C "$DEPLOY" -xzf "$BACKUP/sigaex.war.explodido.antes.tar.gz"
      chown -R enfas:enfas "$WAR"
      ;;
    none)
      echo "Não havia deployment anterior para restaurar."
      return 0
      ;;
  esac
  touch "$DEPLOY/sigaex.war.dodeploy"
  chown enfas:enfas "$DEPLOY/sigaex.war.dodeploy"
  systemctl start "$SERVICE"
}

echo "6/8 - Instalação controlada"
systemctl stop "$SERVICE"
cleanup_markers
rm -rf "$WAR"
install -o enfas -g enfas -m 0644 "$NEW_WAR" "$WAR"
touch "$DEPLOY/sigaex.war.dodeploy"
chown enfas:enfas "$DEPLOY/sigaex.war.dodeploy"

echo "7/8 - Inicialização e confirmação"
if ! systemctl start "$SERVICE"; then rollback; exit 1; fi
DEPLOYED=0
for _ in $(seq 1 72); do
  if [ -f "$DEPLOY/sigaex.war.failed" ]; then
    cat "$DEPLOY/sigaex.war.failed"
    tail -n 200 "$JBOSS_HOME/standalone/log/server.log"
    rollback
    exit 1
  fi
  if [ -f "$DEPLOY/sigaex.war.deployed" ]; then DEPLOYED=1; break; fi
  sleep 5
done
if [ "$DEPLOYED" -ne 1 ]; then
  tail -n 200 "$JBOSS_HOME/standalone/log/server.log"
  rollback
  exit 1
fi

echo "8/8 - Verificação HTTP"
if ! curl --fail --location --silent --show-error --max-time 30 --output /dev/null "$HEALTH_URL"; then
  rollback
  exit 1
fi

echo "PRODUÇÃO IMPLANTADA COM SUCESSO"
echo "Versão: $EXPECTED_VERSION"
echo "Commit: $COMMIT"
echo "Backup: $BACKUP"
echo "WAR: $WAR"
