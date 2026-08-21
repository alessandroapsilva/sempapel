[#--
 Modelo: Ofício
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
[@grupo titulo="Destinatário"]
    [@grupo][@texto titulo="Nome" var="destinatarioNome" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="Cargo/Função" var="destinatarioCargo" largura="35" maxcaracteres="100"/][/@grupo]
    [@grupo][@texto titulo="Empresa ou órgão" var="destinatarioOrganizacao" largura="60" maxcaracteres="150"/][@texto titulo="Cidade/UF" var="destinatarioCidade" largura="25" maxcaracteres="80"/][/@grupo]
    [@grupo][@texto titulo="Vocativo" var="vocativo" largura="45" maxcaracteres="100"/][@selecao titulo="Fecho" var="fecho" opcoes="Atenciosamente;Respeitosamente;Cordialmente"/][/@grupo]
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
[@estiloBrasaoCentralizado tipo="OFÍCIO" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        <p>${vocativo!"Prezado(a) Senhor(a)"},</p><p><strong>${destinatarioNome!}</strong>[#if (destinatarioCargo!"") != ""]<br/>${destinatarioCargo!}[/#if][#if (destinatarioOrganizacao!"") != ""]<br/>${destinatarioOrganizacao!}[/#if][#if (destinatarioCidade!"") != ""]<br/>${destinatarioCidade!}[/#if]</p><p>${fecho!"Atenciosamente"},</p>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
