[#--
 Modelo: Autorização de Compra
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
    [@grupo][@texto titulo="Valor autorizado" var="valorAutorizado" largura="22" maxcaracteres="30" obrigatorio="Sim"/][@texto titulo="Autorizador" var="autorizador" largura="50" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
[/@grupo]
[@grupo titulo="Itens"]
    [@selecao titulo="Quantidade de itens" var="qtdItens" opcoes="1;2;3;4;5;6;7;8;9;10" reler=true idAjax="qtdItensAjax"/]
[/@grupo]
[@grupo depende="qtdItensAjax"]
    [#list 1..((qtdItens!"1")?number) as i]
        [@grupo titulo="Item ${i}"]
            [@texto titulo="Descrição" var="itemDescricao"+i largura="55" maxcaracteres="180" obrigatorio="Sim"/]
            [@texto titulo="Quantidade" var="itemQuantidade"+i largura="8" maxcaracteres="12" obrigatorio="Sim"/]
            [@texto titulo="Unidade" var="itemUnidade"+i largura="10" maxcaracteres="20"/]
        [/@grupo]
        [@grupo]
            [@texto titulo="Valor unitário" var="itemValor"+i largura="15" maxcaracteres="24"/]
            [@texto titulo="Observação" var="itemObs"+i largura="45" maxcaracteres="180"/]
        [/@grupo]
    [/#list]
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
[@estiloBrasaoCentralizado tipo="AUTORIZAÇÃO DE COMPRA" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${tl}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${assunto!}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${interessado!}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${referencia!}</p>[/#if]
        [#if (numeroProcesso!"") != ""]<p><strong>Processo:</strong> ${numeroProcesso!}</p>[/#if]
[#if (fornecedor!"") != ""]<p><strong>Fornecedor:</strong> ${fornecedor!}</p>[/#if]
<p><strong>Valor autorizado:</strong> ${valorAutorizado!}</p><p><strong>Autorizador:</strong> ${autorizador!}</p>
[#if qtdItens??]
        <table width="100%" border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; margin-top: 1em;">
            <tr><th>Item</th><th>Descrição</th><th>Qtd.</th><th>Unidade</th><th>Valor unitário</th><th>Observação</th></tr>
            [#list 1..(qtdItens?number) as i]
                <tr>
                    <td align="center">${i}</td>
                    <td>${.vars['itemDescricao'+i]!}</td>
                    <td align="center">${.vars['itemQuantidade'+i]!}</td>
                    <td align="center">${.vars['itemUnidade'+i]!}</td>
                    <td align="right">${.vars['itemValor'+i]!}</td>
                    <td>${.vars['itemObs'+i]!}</td>
                </tr>
            [/#list]
        </table>
    [/#if]
        <div style="margin-top: 1.2em; text-align: justify;">${conteudo!}</div>
    </div>
[/@estiloBrasaoCentralizado]
[/@documento]
