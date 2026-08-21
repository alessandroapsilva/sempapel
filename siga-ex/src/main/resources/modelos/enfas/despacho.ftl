[#--
 Modelo: Despacho
 Organização: Enfermagem Alessandro Silva
 Padrão: Guia de Macros Freemarker SIGA-DOC
--]
[@entrevista]
[@grupo titulo="Encaminhamento"]
    [@grupo][@texto titulo="Documento de referência" var="documentoReferencia" largura="45" maxcaracteres="100"/][@lotacao titulo="Unidade de destino" var="unidadeDestino"/][/@grupo]
    [@grupo][@selecao titulo="Decisão" var="decisao" opcoes="Ciente;De acordo;Deferido;Indeferido;Para providências;Para análise" obrigatorio="Sim"/][/@grupo]
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
[@estiloBrasaoCentralizado tipo="DESPACHO" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        [#if (documentoReferencia!"") != ""]<p><strong>Referência:</strong> ${documentoReferencia!}</p>[/#if][#if (unidadeDestino!"") != ""]<p><strong>Destino:</strong> ${unidadeDestino!}</p>[/#if]<p><strong>Decisão:</strong> ${decisao!}</p>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
