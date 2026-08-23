# Produção ENFAS Sem Papel — SIGA-DOC 11.5

Este documento define o procedimento de promoção da ENFAS para produção com rastreabilidade, backup e rollback.

## Estado consolidado da branch `release/11.5-enfas`

- Plano de classificação documental administrativo carregado pela V118.
- Catálogo administrativo carregado pela V119.
- Modelos administrativos anteriores preservados pelas V120/V121/V122.
- Núcleo essencial ativo em JSP pela V123: Ofício, Memorando, Despacho, Informação, Parecer, Contrato, Folha Inicial e Processo Administrativo.
- Os JSPs institucionais não duplicam Assunto, classificação, acesso, responsável ou destinatário do `edita.jsp`.
- Numeração pública aleatória de seis dígitos, sem ano na sigla; ano de emissão mantido internamente para auditoria.
- Compatibilidade de leitura com documentos antigos no formato com ano.
- Build com commit Git verdadeiro, backup integral do MySQL e rollback automático do WAR.
- Resíduos temporários e workflows que alteravam JSP automaticamente removidos.

## Numeração

Novo formato:

```text
ENFAS-OFI-503937
```

Documentos antigos mantêm a sigla original. Nunca renumerar documentos já finalizados.

## Implantação na VPS

Use a URL real de produção explicitamente; o script não aceita mais a URL de treinamento por padrão.

```bash
cd /home/enfas/siga_source
git fetch origin
git checkout release/11.5-enfas
git pull --ff-only
chmod +x scripts/deploy-sigaex-production.sh
sudo ENFAS_HEALTH_URL="https://sempapel.enfas.com.br/sigaex/" \
  ./scripts/deploy-sigaex-production.sh release/11.5-enfas
```

Se o domínio definitivo for outro, substitua somente `ENFAS_HEALTH_URL`.

O instalador valida dependências e espaço, faz backup de todos os bancos MySQL, cria clone limpo, confirma os oito JSPs e a V123, compila o SIGA-DOC, salva o WAR atual, implanta no JBoss, verifica o marcador `.deployed`, testa HTTP e restaura o WAR anterior automaticamente se a implantação falhar.

## Checklist obrigatório antes de liberar usuários

### Infraestrutura

- [ ] Domínio definitivo de produção separado de treinamento.
- [ ] TLS válido e renovação automática.
- [ ] `jboss-eap.service` ativo e habilitado no boot.
- [ ] Fuso `America/Sao_Paulo` e NTP ativos.
- [ ] Firewall restrito ao necessário.
- [ ] Rotação de `server.log`, access logs e GC logs.

### Banco

- [ ] Usuário MySQL exclusivo da aplicação; não usar `root` na aplicação.
- [ ] Backup automático diário e cópia fora da VPS.
- [ ] Teste de restauração realizado.
- [ ] Migrations V118 a V123 aplicadas sem erro.
- [ ] Confirmar que os oito modelos ativos possuem `NM_ARQ_MOD=enfas*.jsp` e `ID_ARQ IS NULL` após V123.

### Aplicação

- [ ] Ambiente identificado como Produção.
- [ ] SMTP testado.
- [ ] LDAP/identidade e política de desligamento de usuários revisados.
- [ ] Perfis, lotações e permissões administrativas revisados.
- [ ] Níveis de acesso público, limitado e restrito validados.
- [ ] Classificação, temporalidade e destinação documental validadas.
- [ ] Assinatura, cossignatura, autenticação e verificação pública testadas.
- [ ] Inclusão de documento, anexação, cópia, tramitação e cancelamento testados.

### Segurança

- [ ] Nenhuma senha, chave, certificado, `.env`, dump ou backup no Git.
- [ ] Cookies `Secure`/`HttpOnly` e `SameSite` adequados.
- [ ] Cabeçalhos HTTPS revisados no proxy reverso.
- [ ] Logs de auditoria preservados e protegidos.
- [ ] Política de retenção/descarte e privacidade alinhadas à LGPD.

## Teste de aceite dos modelos

Criar um documento de cada modelo: Ofício, Memorando, Despacho, Informação, Parecer, Contrato, Folha Inicial e Processo Administrativo. Em cada um, testar gravação de rascunho, reabertura para edição, validação dos campos obrigatórios do `edita.jsp`, finalização, assinatura quando aplicável, pesquisa pela sigla, geração de PDF e inclusão/anexação quando aplicável.

## Critérios de aprovação

A promoção só está aprovada quando o build termina com `BUILD SUCCESS`, o JBoss cria `sigaex.war.deployed`, a URL de produção responde sem erro, os oito modelos abrem sem erro JSP, um documento novo recebe número aleatório, assinatura e PDF funcionam, o backup passa em `gzip -t` e não aparecem erros graves novos no `server.log`.

Código pronto não substitui a validação operacional da VPS. Credenciais, DNS/TLS, SMTP, LDAP, backup externo e monitoramento precisam ser confirmados no ambiente real antes da entrada de usuários.
