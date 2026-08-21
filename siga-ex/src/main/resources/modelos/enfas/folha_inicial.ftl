[#--
 Modelo: Folha Inicial
 Organização: Enfermagem Alessandro Silva
 Padrão: Guia de Macros Freemarker SIGA-DOC
--]
[@entrevista]
[@grupo titulo="Identificação"]
    [@grupo]
        [@texto titulo="Assunto" var="assunto" largura="70" maxcaracteres="200" obrigatorio="Sim"/]
    [/@grupo]
    [@grupo]
        [@texto titulo="Interessado" var="interessado" largura="55" maxcaracteres="150"/]
        [@texto titulo="Referência" var="referencia" largura="25" maxcaracteres="80"/]
    [/@grupo]
[/@grupo]
[@grupo titulo="Identificação do processo"]
    [@grupo][@texto titulo="Número do processo" var="numeroProcesso" largura="35" maxcaracteres="60"/][@data titulo="Data de abertura" var="dataAbertura" obrigatorio=true/][/@grupo]
    [@grupo][@texto titulo="Unidade responsável" var="unidadeResponsavel" largura="60" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Objeto do processo" var="objetoProcesso" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]
[@grupo titulo="Conteúdo do documento"]
    [@grupo]
        [@editor titulo="" var="conteudo"/]
    [/@grupo]
[/@grupo]
[@grupo]
    [@selecao titulo="Tamanho da letra" var="tamanhoLetra" opcoes="Normal;Pequeno;Grande"/]
[/@grupo]
[/@entrevista]

[@documento margemEsquerda="3cm" margemDireita="2cm" margemSuperior="1cm" margemInferior="2cm"]
[#if (tamanhoLetra!"Normal") == "Pequeno"]
    [#assign tl="9pt"/]
[#elseif (tamanhoLetra!"Normal") == "Grande"]
    [#assign tl="13pt"/]
[#else]
    [#assign tl="11pt"/]
[/#if]
[@estiloBrasaoCentralizado tipo="FOLHA INICIAL" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        <div style="border:1px solid #333;padding:16px"><p><strong>Processo:</strong> ${numeroProcesso!(doc.codigo!'')}</p><p><strong>Abertura:</strong> ${dataAbertura!}</p><p><strong>Unidade responsável:</strong> ${unidadeResponsavel!}</p><p><strong>Objeto:</strong><br/>${objetoProcesso!}</p></div>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
