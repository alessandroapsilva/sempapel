[#--
 Modelo: Contrato
 Organização: Enfermagem Alessandro Silva
 Padrão: Guia de Macros Freemarker SIGA-DOC
--]
[@entrevista]
[@grupo titulo="Partes e vigência"]
    [@grupo][@texto titulo="Contratada" var="contratada" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="CNPJ/CPF" var="documentoContratada" largura="25" maxcaracteres="24" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Objeto" var="objetoContrato" largura="80" maxcaracteres="220" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Valor" var="valorContrato" largura="22" maxcaracteres="30" obrigatorio="Sim"/][@data titulo="Início da vigência" var="vigenciaInicio" obrigatorio=true/][@data titulo="Fim da vigência" var="vigenciaFim" obrigatorio=true/][/@grupo]
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
[@estiloBrasaoCentralizado tipo="CONTRATO" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        <p><strong>Contratada:</strong> ${contratada!} — ${documentoContratada!}</p><p><strong>Objeto:</strong> ${objetoContrato!}</p><p><strong>Valor:</strong> ${valorContrato!}</p><p><strong>Vigência:</strong> ${vigenciaInicio!} a ${vigenciaFim!}</p>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
