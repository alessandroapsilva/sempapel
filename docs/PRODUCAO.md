# Produção — SIGA-DOC v11.5.100

Esta é a release de produção consolidada da linha 11.5.

## Release oficial

- Versão: `v11.5.100`
- Branch: `release/11.5.100`
- Patch Maven: `100`
- Próximas revisões: `v11.5.101`, `v11.5.102`, ...

A coordenada Maven interna permanece em `11.5-SNAPSHOT` para compatibilidade entre os módulos legados. A revisão pública é controlada por `.mvn/maven.config` e `VERSION`.

## Estado funcional incluído

- Plano de classificação documental administrativo pelas migrations V118+;
- catálogo administrativo e modelos institucionais;
- núcleo essencial em JSP: Ofício, Memorando, Despacho, Informação, Parecer, Contrato, Folha Inicial e Processo Administrativo;
- numeração pública aleatória sem ano na sigla, mantendo o ano internamente para auditoria;
- compatibilidade com documentos antigos;
- backup integral do MySQL antes do deploy;
- build limpo a partir da branch de release;
- validação do manifesto do WAR;
- suporte a backup do `sigaex.war` empacotado ou explodido;
- rollback automático do deployment em falha.

## Deploy

```bash
cd /home/enfas/siga_source
git fetch origin
git checkout release/11.5.100
git pull --ff-only
cat VERSION
chmod +x scripts/deploy-sigaex-production.sh
sudo ENFAS_HEALTH_URL="https://sempapel.enfas.com.br/sigaex/" \
  ./scripts/deploy-sigaex-production.sh release/11.5.100
```

Antes de liberar usuários, confirmar `BUILD SUCCESS`, `sigaex.war.deployed`, resposta HTTP válida, geração de PDF, assinatura, inclusão/anexação de documentos, pesquisa pela nova sigla e ausência de erros graves novos no `server.log`.

## Controle de release

Depois que `v11.5.100` entrar em produção, esta branch deve permanecer estável. Qualquer correção deve ser preparada em `develop/11.5` e publicada em uma nova revisão (`11.5.101`, `11.5.102`, ...), sem reescrever a release anterior.

Consulte `docs/RELEASES.md` para a política completa.
