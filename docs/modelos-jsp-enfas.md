# Modelos JSP institucionais ENFAS

## Decisão de arquitetura

O núcleo documental da ENFAS usa JSP versionado no WAR. Os modelos legados do SIGA permanecem no repositório apenas como referência e não são sobrescritos.

A migration `V123.0__ativa_modelos_jsp_institucionais_enfas.sql` aponta os modelos ativos para os JSPs institucionais e remove apenas a referência ativa ao `ID_ARQ` Freemarker. Os arquivos Freemarker anteriores continuam preservados no banco para rastreabilidade e rollback.

## Núcleo ativo

- Ofício → `enfasOficio.jsp`
- Memorando → `enfasMemorando.jsp`
- Despacho → `enfasDespacho.jsp`
- Informação → `enfasInformacao.jsp`
- Parecer → `enfasParecer.jsp`
- Contrato → `enfasContrato.jsp`
- Folha Inicial → `enfasFolhaInicial.jsp`
- Processo Administrativo → `enfasProcessoAdministrativo.jsp`

## Regras aplicadas

Os JSPs não recriam os campos estruturais já existentes em `edita.jsp`. Assunto, classificação documental, nível de acesso, responsável pela assinatura e destinatário continuam sendo controlados pelo fluxo nativo do SIGA. O modelo usa esses dados somente para compor a apresentação final quando aplicável.

O texto livre permanece no editor do próprio modelo. Todos os novos JSPs usam UTF-8, HTML simples compatível com o gerador de PDF do SIGA e o include nativo de assinatura.

## Compatibilidade e rollback

Os JSPs antigos (`oficio.jsp`, `memorando.jsp`, `despacho.jsp` e demais modelos históricos) não foram alterados. Para rollback de modelo, basta restaurar o banco anterior ao deploy ou reatribuir o `ID_ARQ` preservado pelo backup/migration anterior.

Antes da liberação, validar criação, gravação, finalização, assinatura e geração de PDF para os oito modelos.
