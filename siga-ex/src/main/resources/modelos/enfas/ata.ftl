[#--
 Modelo: Ata
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
[@grupo titulo="Reunião"]
    [@grupo][@data titulo="Data da reunião" var="dataReuniao" obrigatorio=true/][@texto titulo="Horário" var="horario" largura="10" maxcaracteres="10" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Local" var="local" largura="70" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Participantes" var="participantes" colunas="90" linhas="4" obrigatorio=true/]
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
[@estiloBrasaoCentralizado tipo="ATA" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        <p><strong>Data e horário:</strong> ${dataReuniao!} às ${horario!}</p><p><strong>Local:</strong> ${local!}</p><p><strong>Participantes:</strong><br/>${participantes!}</p>
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
