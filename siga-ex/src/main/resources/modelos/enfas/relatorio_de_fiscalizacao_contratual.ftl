[#--
 Modelo: Relatório de Fiscalização Contratual
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
[@grupo titulo="Processo de compra"]
    [@grupo][@texto titulo="Número/Referência" var="numeroProcesso" largura="30" maxcaracteres="60"/][@texto titulo="Fornecedor" var="fornecedor" largura="50" maxcaracteres="150"/][/@grupo]
    [@grupo][@texto titulo="Contrato" var="numeroContrato" largura="30" maxcaracteres="60" obrigatorio="Sim"/][@texto titulo="Período fiscalizado" var="periodoFiscalizado" largura="35" maxcaracteres="80" obrigatorio="Sim"/][/@grupo][@selecao titulo="Resultado" var="resultadoFiscalizacao" opcoes="Regular;Regular com ressalvas;Irregular"/][@memo titulo="Ocorrências e providências" var="ocorrencias" colunas="90" linhas="5" obrigatorio=true/]
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
[@estiloBrasaoCentralizado tipo="RELATÓRIO DE FISCALIZAÇÃO CONTRATUAL" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        [#if (numeroProcesso!"") != ""]<p><strong>Processo:</strong> ${numeroProcesso!}</p>[/#if]
[#if (fornecedor!"") != ""]<p><strong>Fornecedor:</strong> ${fornecedor!}</p>[/#if]
<p><strong>Contrato:</strong> ${numeroContrato!}</p><p><strong>Período:</strong> ${periodoFiscalizado!}</p><p><strong>Resultado:</strong> ${resultadoFiscalizacao!}</p><p><strong>Ocorrências e providências:</strong><br/>${ocorrencias!}</p>

        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
