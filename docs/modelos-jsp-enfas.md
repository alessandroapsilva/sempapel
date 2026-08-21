# Curadoria dos modelos JSP para a ENFAS

## Resultado do inventário

A pasta legada contém 401 modelos JSP. O acervo foi criado principalmente para
órgãos do Judiciário e não deve ser ativado integralmente em uma empresa
privada. A varredura encontrou:

- 92 arquivos com referência à Justiça Federal;
- 60 arquivos com referência a Tribunal Regional;
- 57 arquivos com referência a Juiz Federal;
- 40 arquivos com siglas de TRFs;
- 34 arquivos com referência ao Conselho da Justiça;
- 257 arquivos ainda declarados como ISO-8859-1;
- 400 arquivos com scriptlets ou diretivas JSP legadas.

## Núcleo empresarial mantido

Os modelos essenciais foram recriados em Freemarker e instalados pela migration
V121, preservando o motor JSP apenas onde a lógica dinâmica do SIGA exige:

- Ofício;
- Memorando;
- Despacho;
- Informação;
- Parecer;
- Contrato;
- Folha Inicial;
- Processo Administrativo;
- Boletim Interno (JSP dinâmico).

Ata Geral e Termo Geral tiveram erros históricos de cópia corrigidos. O Boletim
Interno deixou de trazer nomes de servidores e setores judiciais fixos.

## Critério para os demais JSPs

Modelos de atos judiciais, alvarás, corregedoria, magistratura, TRFs, Conselho da
Justiça e benefícios de servidores públicos permanecem no código apenas como
legado e não devem ser cadastrados para uso da ENFAS. Modelos administrativos
que venham a ser necessários devem ser convertidos individualmente, com espécie,
classificação, temporalidade e campos revisados antes da ativação.

## Implantação

`V121.0__atualiza_modelos_essenciais_enfas.sql` cria uma nova versão de arquivo
para não sobrescrever o conteúdo legado, atualiza o modelo ativo e é idempotente
por hash. A migration V119 deve ter sido aplicada antes dela.
