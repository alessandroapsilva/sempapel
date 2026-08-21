[#--
 Modelo: Cadastro de Fornecedor
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
    [@grupo][@texto titulo="Razão social" var="razaoSocial" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="CNPJ/CPF" var="cnpjCpf" largura="24" maxcaracteres="24" obrigatorio="Sim"/][/@grupo][@grupo][@texto titulo="Contato" var="contato" largura="45" maxcaracteres="100"/][@texto titulo="E-mail" var="email" largura="45" maxcaracteres="120"/][/@grupo]
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
[@estiloBrasaoCentralizado tipo="CADASTRO DE FORNECEDOR" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        [#if (numeroProcesso!"") != ""]<p><strong>Processo:</strong> ${numeroProcesso!}</p>[/#if]
[#if (fornecedor!"") != ""]<p><strong>Fornecedor:</strong> ${fornecedor!}</p>[/#if]
<p><strong>Razão social:</strong> ${razaoSocial!}</p><p><strong>CNPJ/CPF:</strong> ${cnpjCpf!}</p><p><strong>Contato:</strong> ${contato!} - ${email!}</p>

        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
