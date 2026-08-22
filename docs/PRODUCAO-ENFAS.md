# Produção ENFAS Sem Papel — SIGA-DOC 11.5

Este documento define o mínimo obrigatório para promover o ambiente da ENFAS de homologação para produção com rastreabilidade e possibilidade de rollback.

## Estado consolidado desta branch

- Plano de classificação documental administrativo carregado pelas migrations V118.
- Modelos administrativos ENFAS carregados pelas migrations V120 e V121.
- Numeração pública aleatória de seis dígitos, sem ano na sigla.
- Ano de emissão mantido internamente para auditoria.
- Compatibilidade de leitura com documentos antigos no formato com ano.
- Exibição e pesquisa do novo formato tratadas no domínio.
- Build com commit Git verdadeiro.
- Implantação limpa, sem reaplicar patches locais de JSP.
- Rotina de backup integral do MySQL antes do deploy.
- Rollback automático do WAR se o JBoss rejeitar a implantação.
- Resíduos temporários e workflows que alteravam JSP automaticamente removidos.

## Regra de numeração

Documentos novos finalizados usam o formato:

```text
ENFAS-OFI-503937
```

Documentos antigos mantêm o formato original:

```text
ENFAS-OFI-2026/00006
```

Nunca renumerar registros já finalizados. O ano continua armazenado em `EX_DOCUMENTO.ANO_EMISSAO`.

## Implantação

Na VPS:

```bash
cd /home/enfas/siga_source
git fetch origin
git checkout feat/classificacoes-sp-uape-2026
git pull --ff-only
chmod +x scripts/deploy-sigaex-production.sh
sudo ./scripts/deploy-sigaex-production.sh feat/classificacoes-sp-uape-2026
```

O instalador:

1. valida espaço e dependências;
2. faz backup de todos os bancos MySQL;
3. cria clone limpo;
4. valida as correções críticas;
5. compila o SIGA-DOC;
6. salva o WAR atual;
7. implanta e confirma o marcador do JBoss;
8. testa a URL;
9. restaura o WAR anterior automaticamente em caso de falha.

Para outra URL de produção:

```bash
sudo ENFAS_HEALTH_URL="https://sempapel.enfas.com.br/sigaex/" \
  ./scripts/deploy-sigaex-production.sh feat/classificacoes-sp-uape-2026
```

## Checklist obrigatório antes da liberação

### Infraestrutura

- [ ] Definir domínio definitivo de produção, separado de `treinamento`.
- [ ] TLS válido e renovação automática.
- [ ] JBoss executado exclusivamente pelo serviço `jboss-eap.service`.
- [ ] Servidor com horário `America/Sao_Paulo` e NTP ativo.
- [ ] Firewall permitindo somente SSH administrativo, HTTP e HTTPS necessários.
- [ ] Usuário SSH individual; não compartilhar senha de root.
- [ ] Diretórios do JBoss pertencentes ao usuário de serviço `enfas`.
- [ ] Rotação configurada para `server.log`, access logs e GC logs.

### Banco de dados

- [ ] Criar usuário MySQL exclusivo da aplicação; não usar `root`.
- [ ] Senha armazenada somente na configuração protegida da VPS.
- [ ] Backup automático diário e cópia fora da VPS.
- [ ] Política de retenção definida.
- [ ] Teste de restauração realizado em ambiente separado.
- [ ] Validar migrations aplicadas e ausência de duplicidades.
- [ ] Monitorar espaço, conexões, locks e consultas lentas.

### Aplicação

- [ ] Configurar ambiente como `Produção`, removendo a identificação de homologação.
- [ ] Desativar páginas e recursos de diagnóstico não necessários.
- [ ] Configurar SMTP e testar notificações.
- [ ] Confirmar LDAP/identidade e política de desligamento de usuários.
- [ ] Revisar perfis, lotações e permissões administrativas.
- [ ] Validar níveis de acesso: público, limitado e restrito.
- [ ] Validar classificação, temporalidade e destinação documental.
- [ ] Validar antivírus e limites para anexos.
- [ ] Testar assinatura, cossignatura, autenticação e verificação pública.
- [ ] Testar inclusão de documento, anexação, cópia, tramitação e cancelamento.
- [ ] Confirmar que novos documentos usam número aleatório e documentos antigos permanecem inalterados.

### Segurança e conformidade

- [ ] Nenhuma senha, chave, certificado, `.env`, dump ou backup no Git.
- [ ] Cookies com `Secure`, `HttpOnly` e política `SameSite` adequada.
- [ ] Cabeçalhos HTTPS revisados no proxy reverso.
- [ ] Acesso administrativo registrado e restrito.
- [ ] Logs de auditoria preservados e protegidos contra alteração.
- [ ] Política interna de retenção e descarte aprovada.
- [ ] Aviso de privacidade e tratamento de dados alinhados à LGPD.
- [ ] Plano de resposta a incidente e responsável técnico definidos.

## Teste de aceite

Criar documentos novos de pelo menos estas espécies:

- Ofício;
- Memorando;
- Informação;
- Despacho;
- Parecer;
- Contrato;
- Processo Administrativo.

Para cada documento:

1. gravar como rascunho;
2. editar e validar os campos obrigatórios;
3. finalizar;
4. assinar;
5. pesquisar pela nova sigla;
6. gerar impressão/PDF;
7. incluir anexo ou documento relacionado;
8. conferir classificação, acesso, data e trilha de auditoria.

## Critérios de aprovação

A promoção está aprovada somente quando:

- o build termina com `BUILD SUCCESS`;
- o JBoss cria `sigaex.war.deployed`;
- a URL responde sem erro;
- um documento novo recebe número aleatório;
- assinatura e PDF funcionam;
- o backup passa em `gzip -t`;
- o rollback foi ensaiado;
- nenhum erro grave novo aparece no `server.log`.

## Observação

Código pronto não substitui a validação do ambiente. Domínio, TLS, credenciais, SMTP, LDAP, backup externo e monitoramento são controles operacionais da VPS e devem ser conferidos antes de atender usuários reais.
