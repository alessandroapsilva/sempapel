[#--
 Modelo: Processo Administrativo
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
[@grupo titulo="Abertura do processo"]
    [@grupo][@selecao titulo="Área" var="areaProcesso" opcoes="Administrativo;Compras e contratos;Financeiro;Recursos humanos;Patrimônio;Tecnologia;Proteção de dados;Qualidade" obrigatorio="Sim"/][@texto titulo="Unidade responsável" var="unidadeResponsavel" largura="45" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Objeto do processo" var="objetoProcesso" colunas="90" linhas="4" obrigatorio=true/]
    [@texto titulo="Interessado principal" var="interessadoPrincipal" largura="60" maxcaracteres="150"/]
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
[@estiloBrasaoCentralizado tipo="PROCESSO ADMINISTRATIVO" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        <div style="border:2px solid #333;padding:18px"><p><strong>Número:</strong> ${doc.codigo!}</p><p><strong>Data de abertura:</strong> ${doc.dtDocDDMMYYYY!}</p><p><strong>Área:</strong> ${areaProcesso!}</p><p><strong>Unidade responsável:</strong> ${unidadeResponsavel!}</p>[#if (interessadoPrincipal!"") != ""]<p><strong>Interessado:</strong> ${interessadoPrincipal!}</p>[/#if]<p><strong>Objeto:</strong><br/>${objetoProcesso!}</p></div>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
