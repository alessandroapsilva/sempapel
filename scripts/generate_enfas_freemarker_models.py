#!/usr/bin/env python3
"""Gera os modelos Freemarker ENFAS e a migration MySQL que os instala."""

from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "siga-ex/src/main/resources/modelos/enfas"
MIGRATION = ROOT / "siga-ex/src/main/resources/db/mysql/sigaex/V120.0__modelos_freemarker_administrativos_enfas.sql"


def common_interview(extra: str = "", body_title: str = "Conteúdo do documento") -> str:
    return f'''[@grupo titulo="Identificação"]
    [@grupo]
        [@texto titulo="Assunto" var="assunto" largura="70" maxcaracteres="200" obrigatorio="Sim"/]
    [/@grupo]
    [@grupo]
        [@texto titulo="Interessado" var="interessado" largura="55" maxcaracteres="150"/]
        [@texto titulo="Referência" var="referencia" largura="25" maxcaracteres="80"/]
    [/@grupo]
[/@grupo]
{extra}
[@grupo titulo="{body_title}"]
    [@grupo]
        [@editor titulo="" var="conteudo"/]
    [/@grupo]
[/@grupo]
[@grupo]
    [@selecao titulo="Tamanho da letra" var="tamanhoLetra" opcoes="Normal;Pequeno;Grande"/]
[/@grupo]'''


def common_document(label: str, extra_html: str = "") -> str:
    return f'''[#if (tamanhoLetra!"Normal") == "Pequeno"]
    [#assign tl="9pt"/]
[#elseif (tamanhoLetra!"Normal") == "Grande"]
    [#assign tl="13pt"/]
[#else]
    [#assign tl="11pt"/]
[/#if]
[@estiloBrasaoCentralizado tipo="{label}" tamanhoLetra=tl formatarOrgao=true numeracaoCentralizada=false dataAntesDaAssinatura=true]
    <div style="font-family: Arial; font-size: ${{tl}}; line-height: 1.5;">
        [#if (assunto!"") != ""]<p><strong>Assunto:</strong> ${{assunto!}}</p>[/#if]
        [#if (interessado!"") != ""]<p><strong>Interessado:</strong> ${{interessado!}}</p>[/#if]
        [#if (referencia!"") != ""]<p><strong>Referência:</strong> ${{referencia!}}</p>[/#if]
        {extra_html}
        <div style="margin-top: 1.2em; text-align: justify;">${{conteudo!}}</div>
    </div>
[/@estiloBrasaoCentralizado]'''


def template(description: str, interview: str, document: str) -> str:
    rendered = f'''[#--
 Modelo: {description}
 Organização: Enfermagem Alessandro Silva
 Padrão: Guia de Macros Freemarker SIGA-DOC
--]
[@entrevista]
{interview}
[/@entrevista]

[@documento margemEsquerda="3cm" margemDireita="2cm" margemSuperior="1cm" margemInferior="2cm"]
{document}
[/@documento]
'''
    return "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"


def generic(name: str, label: str, classification: str | None = None, extra: str = "", extra_html: str = "") -> dict:
    return {
        "name": name,
        "label": label,
        "classification": classification,
        "content": template(name, common_interview(extra), common_document(label, extra_html)),
    }


def item_table_interview(kind: str, max_items: int = 10) -> str:
    options = ";".join(str(i) for i in range(1, max_items + 1))
    return f'''[@grupo titulo="Itens"]
    [@selecao titulo="Quantidade de itens" var="qtdItens" opcoes="{options}" reler=true idAjax="qtdItensAjax"/]
[/@grupo]
[@grupo depende="qtdItensAjax"]
    [#list 1..((qtdItens!"1")?number) as i]
        [@grupo titulo="Item ${{i}}"]
            [@texto titulo="Descrição" var="itemDescricao"+i largura="55" maxcaracteres="180" obrigatorio="Sim"/]
            [@texto titulo="Quantidade" var="itemQuantidade"+i largura="8" maxcaracteres="12" obrigatorio="Sim"/]
            [@texto titulo="Unidade" var="itemUnidade"+i largura="10" maxcaracteres="20"/]
        [/@grupo]
        [@grupo]
            [@texto titulo="Valor unitário" var="itemValor"+i largura="15" maxcaracteres="24"/]
            [@texto titulo="Observação" var="itemObs"+i largura="45" maxcaracteres="180"/]
        [/@grupo]
    [/#list]
[/@grupo]'''


def item_table_html() -> str:
    return '''[#if qtdItens??]
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
    [/#if]'''


MODELS = [
    generic("Ata", "ATA", "001.03.01.002", '''[@grupo titulo="Reunião"]
    [@grupo][@data titulo="Data da reunião" var="dataReuniao" obrigatorio=true/][@texto titulo="Horário" var="horario" largura="10" maxcaracteres="10" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Local" var="local" largura="70" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Participantes" var="participantes" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]''', '''<p><strong>Data e horário:</strong> ${dataReuniao!} às ${horario!}</p><p><strong>Local:</strong> ${local!}</p><p><strong>Participantes:</strong><br/>${participantes!}</p>'''),
    generic("Aviso", "AVISO", "006.01.10.001"),
    generic("Carta", "CARTA", "006.01.10.003", '''[@grupo titulo="Destinatário"]
    [@grupo][@texto titulo="Nome" var="nomeDestinatario" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="Tratamento" var="tratamento" largura="20" maxcaracteres="40"/][/@grupo]
    [@grupo][@texto titulo="Endereço" var="endereco" largura="80" maxcaracteres="200"/][/@grupo]
[/@grupo]''', '''<p><strong>Destinatário:</strong> ${(tratamento!"")} ${(nomeDestinatario!"")}</p>[#if (endereco!"") != ""]<p>${endereco!}</p>[/#if]'''),
    generic("Circular", "CIRCULAR", "006.01.10.001"),
    generic("Comunicado", "COMUNICADO", "006.01.10.001"),
    generic("Comunicação Interna", "COMUNICAÇÃO INTERNA", "006.01.10.001"),
    generic("Declaração", "DECLARAÇÃO", "006.01.09.002", '''[@grupo titulo="Declarante"]
    [@grupo][@texto titulo="Finalidade" var="finalidade" largura="70" maxcaracteres="180" obrigatorio="Sim"/][/@grupo]
[/@grupo]''', '''<p><strong>Finalidade:</strong> ${finalidade!}</p>'''),
    generic("Certidão Geral", "CERTIDÃO", "006.01.09.002", '''[@grupo titulo="Certificação"]
    [@grupo][@texto titulo="Documento ou fato certificado" var="fatoCertificado" largura="80" maxcaracteres="220" obrigatorio="Sim"/][/@grupo]
[/@grupo]''', '''<p><strong>Certifica-se:</strong> ${fatoCertificado!}</p>'''),
    generic("Nota Técnica", "NOTA TÉCNICA", None, '''[@grupo titulo="Análise"]
    [@grupo][@texto titulo="Unidade demandante" var="unidadeDemandante" largura="60" maxcaracteres="120"/][/@grupo]
    [@memo titulo="Conclusão" var="conclusao" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]''', '''[#if (unidadeDemandante!"") != ""]<p><strong>Unidade demandante:</strong> ${unidadeDemandante!}</p>[/#if]<p><strong>Conclusão:</strong><br/>${conclusao!}</p>'''),
    generic("Ordem de Serviço", "ORDEM DE SERVIÇO", "001.01.01.001", '''[@grupo titulo="Execução"]
    [@grupo][@texto titulo="Responsável" var="responsavel" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@data titulo="Prazo" var="prazo"/][/@grupo]
[/@grupo]''', '''<p><strong>Responsável:</strong> ${responsavel!}</p>[#if (prazo!"") != ""]<p><strong>Prazo:</strong> ${prazo!}</p>[/#if]'''),
    generic("Pauta de Reunião", "PAUTA DE REUNIÃO", "001.03.01.013", '''[@grupo titulo="Reunião"]
    [@grupo][@data titulo="Data" var="dataReuniao" obrigatorio=true/][@texto titulo="Horário" var="horario" largura="10" maxcaracteres="10"/][/@grupo]
    [@grupo][@texto titulo="Local" var="local" largura="70" maxcaracteres="150"/][/@grupo]
[/@grupo]''', '''<p><strong>Data:</strong> ${dataReuniao!} ${horario!}</p>[#if (local!"") != ""]<p><strong>Local:</strong> ${local!}</p>[/#if]'''),
    generic("Política Interna", "POLÍTICA INTERNA", "001.01.01.001", '''[@grupo titulo="Controle"]
    [@grupo][@texto titulo="Versão" var="versao" largura="12" maxcaracteres="20" obrigatorio="Sim"/][@data titulo="Vigência" var="vigencia" obrigatorio=true/][/@grupo]
    [@grupo][@texto titulo="Responsável pela aprovação" var="aprovador" largura="60" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
[/@grupo]''', '''<p><strong>Versão:</strong> ${versao!} &nbsp; <strong>Vigência:</strong> ${vigencia!}</p><p><strong>Aprovação:</strong> ${aprovador!}</p>'''),
    generic("Procedimento Operacional Padrão", "PROCEDIMENTO OPERACIONAL PADRÃO", "001.01.01.001", '''[@grupo titulo="Controle do procedimento"]
    [@grupo][@texto titulo="Código" var="codigoPop" largura="18" maxcaracteres="30" obrigatorio="Sim"/][@texto titulo="Versão" var="versao" largura="12" maxcaracteres="20" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Responsável" var="responsavel" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@data titulo="Revisão prevista" var="revisao"/][/@grupo]
[/@grupo]''', '''<p><strong>Código:</strong> ${codigoPop!} &nbsp; <strong>Versão:</strong> ${versao!}</p><p><strong>Responsável:</strong> ${responsavel!}</p>[#if (revisao!"") != ""]<p><strong>Revisão prevista:</strong> ${revisao!}</p>[/#if]'''),
    generic("Relatório", "RELATÓRIO", None, '''[@grupo titulo="Período"]
    [@grupo][@data titulo="Data inicial" var="dataInicial"/][@data titulo="Data final" var="dataFinal"/][/@grupo]
    [@memo titulo="Conclusão" var="conclusao" colunas="90" linhas="4"/]
[/@grupo]''', '''[#if (dataInicial!"") != "" || (dataFinal!"") != ""]<p><strong>Período:</strong> ${dataInicial!} a ${dataFinal!}</p>[/#if][#if (conclusao!"") != ""]<p><strong>Conclusão:</strong><br/>${conclusao!}</p>[/#if]'''),
    generic("Requerimento", "REQUERIMENTO", "006.01.10.005", '''[@grupo titulo="Requerente"]
    [@grupo][@texto titulo="Nome" var="requerente" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="CPF/CNPJ" var="documentoRequerente" largura="22" maxcaracteres="24"/][/@grupo]
    [@grupo][@texto titulo="Pedido" var="pedido" largura="80" maxcaracteres="220" obrigatorio="Sim"/][/@grupo]
[/@grupo]''', '''<p><strong>Requerente:</strong> ${requerente!} ${documentoRequerente!}</p><p><strong>Pedido:</strong> ${pedido!}</p>'''),
    generic("Solicitação", "SOLICITAÇÃO", None, '''[@grupo titulo="Solicitação"]
    [@grupo][@texto titulo="Unidade destinatária" var="unidadeDestinataria" largura="60" maxcaracteres="150" obrigatorio="Sim"/][@data titulo="Prazo desejado" var="prazoDesejado"/][/@grupo]
[/@grupo]''', '''<p><strong>Unidade destinatária:</strong> ${unidadeDestinataria!}</p>[#if (prazoDesejado!"") != ""]<p><strong>Prazo desejado:</strong> ${prazoDesejado!}</p>[/#if]'''),
    generic("Termo Geral", "TERMO", None, '''[@grupo titulo="Partes"]
    [@grupo][@texto titulo="Primeira parte" var="parteUm" largura="60" maxcaracteres="180" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Segunda parte" var="parteDois" largura="60" maxcaracteres="180"/][/@grupo]
[/@grupo]''', '''<p><strong>Primeira parte:</strong> ${parteUm!}</p>[#if (parteDois!"") != ""]<p><strong>Segunda parte:</strong> ${parteDois!}</p>[/#if]'''),
    generic("Termo de Referência", "TERMO DE REFERÊNCIA", "004.01.04.002", '''[@grupo titulo="Contratação"]
    [@grupo][@texto titulo="Objeto" var="objeto" largura="80" maxcaracteres="220" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Justificativa" var="justificativa" colunas="90" linhas="4" obrigatorio=true/]
    [@memo titulo="Critérios de aceitação" var="criterios" colunas="90" linhas="4"/]
[/@grupo]''', '''<p><strong>Objeto:</strong> ${objeto!}</p><p><strong>Justificativa:</strong><br/>${justificativa!}</p>[#if (criterios!"") != ""]<p><strong>Critérios de aceitação:</strong><br/>${criterios!}</p>[/#if]'''),
]


def procurement(name: str, label: str, classification: str, fields: str = "", fields_html: str = "", items: bool = True) -> dict:
    extra = f'''[@grupo titulo="Processo de compra"]
    [@grupo][@texto titulo="Número/Referência" var="numeroProcesso" largura="30" maxcaracteres="60"/][@texto titulo="Fornecedor" var="fornecedor" largura="50" maxcaracteres="150"/][/@grupo]
    {fields}
[/@grupo]
{item_table_interview("item") if items else ""}'''
    html = f'''[#if (numeroProcesso!"") != ""]<p><strong>Processo:</strong> ${{numeroProcesso!}}</p>[/#if]
[#if (fornecedor!"") != ""]<p><strong>Fornecedor:</strong> ${{fornecedor!}}</p>[/#if]
{fields_html}
{item_table_html() if items else ""}'''
    return generic(name, label, classification, extra, html)


MODELS.extend([
    procurement("Solicitação de Compra", "SOLICITAÇÃO DE COMPRA", "004.01.04.002", '''[@grupo][@texto titulo="Centro de custo" var="centroCusto" largura="35" maxcaracteres="80"/][@data titulo="Necessidade até" var="dataNecessidade"/][/@grupo][@memo titulo="Justificativa da compra" var="justificativaCompra" colunas="90" linhas="4" obrigatorio=true/]''', '''<p><strong>Centro de custo:</strong> ${centroCusto!}</p><p><strong>Justificativa:</strong><br/>${justificativaCompra!}</p>'''),
    procurement("Cotação de Preços", "COTAÇÃO DE PREÇOS", "004.01.04.002", '''[@grupo][@data titulo="Validade" var="validade"/][@texto titulo="Condição de pagamento" var="condicaoPagamento" largura="45" maxcaracteres="100"/][/@grupo]''', '''<p><strong>Validade:</strong> ${validade!} &nbsp; <strong>Pagamento:</strong> ${condicaoPagamento!}</p>'''),
    procurement("Mapa Comparativo de Preços", "MAPA COMPARATIVO DE PREÇOS", "004.01.04.002", '''[@memo titulo="Fornecedores consultados" var="fornecedoresConsultados" colunas="90" linhas="4" obrigatorio=true/][@memo titulo="Critério e conclusão" var="criterioConclusao" colunas="90" linhas="4" obrigatorio=true/]''', '''<p><strong>Fornecedores consultados:</strong><br/>${fornecedoresConsultados!}</p><p><strong>Critério e conclusão:</strong><br/>${criterioConclusao!}</p>'''),
    procurement("Autorização de Compra", "AUTORIZAÇÃO DE COMPRA", "004.01.04.002", '''[@grupo][@texto titulo="Valor autorizado" var="valorAutorizado" largura="22" maxcaracteres="30" obrigatorio="Sim"/][@texto titulo="Autorizador" var="autorizador" largura="50" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]''', '''<p><strong>Valor autorizado:</strong> ${valorAutorizado!}</p><p><strong>Autorizador:</strong> ${autorizador!}</p>'''),
    procurement("Pedido de Compra", "PEDIDO DE COMPRA", "004.03.02.002", '''[@grupo][@texto titulo="Condição de pagamento" var="condicaoPagamento" largura="45" maxcaracteres="100"/][@data titulo="Previsão de entrega" var="previsaoEntrega"/][/@grupo]''', '''<p><strong>Condição de pagamento:</strong> ${condicaoPagamento!}</p><p><strong>Previsão de entrega:</strong> ${previsaoEntrega!}</p>'''),
    procurement("Ordem de Compra", "ORDEM DE COMPRA", "004.01.04.002", '''[@grupo][@texto titulo="CNPJ do fornecedor" var="cnpjFornecedor" largura="24" maxcaracteres="24"/][@data titulo="Entrega prevista" var="entregaPrevista"/][/@grupo]''', '''<p><strong>CNPJ:</strong> ${cnpjFornecedor!} &nbsp; <strong>Entrega prevista:</strong> ${entregaPrevista!}</p>'''),
    procurement("Atestado de Recebimento", "ATESTADO DE RECEBIMENTO", "004.03.03.001", '''[@grupo][@data titulo="Data do recebimento" var="dataRecebimento" obrigatorio=true/][@selecao titulo="Condição" var="condicao" opcoes="Recebido integralmente;Recebido parcialmente;Recebido com ressalvas"/][/@grupo][@memo titulo="Ressalvas" var="ressalvas" colunas="90" linhas="3"/]''', '''<p><strong>Recebimento:</strong> ${dataRecebimento!} - ${condicao!}</p>[#if (ressalvas!"") != ""]<p><strong>Ressalvas:</strong><br/>${ressalvas!}</p>[/#if]'''),
    procurement("Cadastro de Fornecedor", "CADASTRO DE FORNECEDOR", "004.01.03.001", '''[@grupo][@texto titulo="Razão social" var="razaoSocial" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="CNPJ/CPF" var="cnpjCpf" largura="24" maxcaracteres="24" obrigatorio="Sim"/][/@grupo][@grupo][@texto titulo="Contato" var="contato" largura="45" maxcaracteres="100"/][@texto titulo="E-mail" var="email" largura="45" maxcaracteres="120"/][/@grupo]''', '''<p><strong>Razão social:</strong> ${razaoSocial!}</p><p><strong>CNPJ/CPF:</strong> ${cnpjCpf!}</p><p><strong>Contato:</strong> ${contato!} - ${email!}</p>''', False),
    procurement("Avaliação de Fornecedor", "AVALIAÇÃO DE FORNECEDOR", "004.01.03.001", '''[@grupo][@selecao titulo="Qualidade" var="qualidade" opcoes="Excelente;Bom;Regular;Ruim"/][@selecao titulo="Prazo" var="prazoAvaliacao" opcoes="No prazo;Com atraso;Não entregue"/][/@grupo][@memo titulo="Conclusão da avaliação" var="conclusaoAvaliacao" colunas="90" linhas="4" obrigatorio=true/]''', '''<p><strong>Qualidade:</strong> ${qualidade!} &nbsp; <strong>Prazo:</strong> ${prazoAvaliacao!}</p><p><strong>Conclusão:</strong><br/>${conclusaoAvaliacao!}</p>''', False),
    procurement("Relatório de Fiscalização Contratual", "RELATÓRIO DE FISCALIZAÇÃO CONTRATUAL", "004.01.01.001", '''[@grupo][@texto titulo="Contrato" var="numeroContrato" largura="30" maxcaracteres="60" obrigatorio="Sim"/][@texto titulo="Período fiscalizado" var="periodoFiscalizado" largura="35" maxcaracteres="80" obrigatorio="Sim"/][/@grupo][@selecao titulo="Resultado" var="resultadoFiscalizacao" opcoes="Regular;Regular com ressalvas;Irregular"/][@memo titulo="Ocorrências e providências" var="ocorrencias" colunas="90" linhas="5" obrigatorio=true/]''', '''<p><strong>Contrato:</strong> ${numeroContrato!}</p><p><strong>Período:</strong> ${periodoFiscalizado!}</p><p><strong>Resultado:</strong> ${resultadoFiscalizacao!}</p><p><strong>Ocorrências e providências:</strong><br/>${ocorrencias!}</p>''', False),
])


def sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def generate() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for old_model in MODEL_DIR.glob("*.ftl"):
        old_model.unlink()
    names = [model["name"] for model in MODELS]
    if len(names) != len(set(names)):
        raise ValueError("Há nomes de modelos duplicados")
    sql = [
        "-- Modelos Freemarker administrativos da Enfermagem Alessandro Silva.",
        "-- Gerado por scripts/generate_enfas_freemarker_models.py.",
        "-- Requer V119.0 (catálogo de espécies documentais).",
        "",
        "START TRANSACTION;",
        "",
    ]
    for model in MODELS:
        slug = unicodedata.normalize("NFKD", model["name"].lower()).encode("ascii", "ignore").decode("ascii")
        filename = slug.replace(" ", "_") + ".ftl"
        content = model["content"].strip() + "\n"
        (MODEL_DIR / filename).write_text(content, encoding="utf-8")
        payload = content.encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        classification = "NULL" if model["classification"] is None else f"(SELECT ID_CLASSIFICACAO FROM ex_classificacao WHERE HIS_ATIVO=1 AND codificacao={sql_quote(model['classification'])} LIMIT 1)"
        sql.extend([
            f"-- {model['name']}",
            "SET @id_arq = NULL;",
            "INSERT INTO corporativo.cp_arquivo (ID_ORGAO_USU, CONTEUDO_TP_ARQ, TP_ARMAZENAMENTO, CAMINHO, TAMANHO_ARQ, HASH_SHA256, NOME_ARQ)",
            f"SELECT NULL, 'template/freemarker', 'TABELA', NULL, {len(payload)}, '{digest}', {sql_quote(filename)}",
            "WHERE NOT EXISTS (SELECT 1 FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD=" + sql_quote(model["name"]) + ");",
            "SET @criou_arq = ROW_COUNT();",
            "SET @id_arq = IF(@criou_arq=1, LAST_INSERT_ID(), NULL);",
            "INSERT INTO corporativo.cp_arquivo_blob (ID_ARQ_BLOB, CONTEUDO_ARQ_BLOB)",
            f"SELECT @id_arq, UNHEX('{payload.hex()}') WHERE @id_arq IS NOT NULL;",
            "INSERT INTO ex_modelo (NM_MOD, DESC_MOD, ID_ARQ, NM_ARQ_MOD, ID_CLASSIFICACAO, ID_FORMA_DOC, ID_CLASS_CRIACAO_VIA, ID_NIVEL_ACESSO, HIS_ID_INI, HIS_DT_INI, HIS_DT_FIM, HIS_IDC_INI, HIS_IDC_FIM, HIS_ATIVO, NM_DIRETORIO, HIS_IDE, MARCA_DAGUA, EXTENSOES_ARQUIVO)",
            f"SELECT {sql_quote(model['name'])}, {sql_quote('Modelo administrativo - Enfermagem Alessandro Silva')}, @id_arq, NULL, {classification}, f.ID_FORMA_DOC, NULL, 1, NULL, CURRENT_TIMESTAMP, NULL, NULL, NULL, 1, 'ENFAS', NULL, NULL, NULL",
            f"FROM ex_forma_documento f WHERE f.DESCR_FORMA_DOC={sql_quote(model['name'] if model['name'] != 'Certidão Geral' and model['name'] != 'Termo Geral' else ('Certidão' if model['name'] == 'Certidão Geral' else 'Termo'))}",
            "  AND @id_arq IS NOT NULL LIMIT 1;",
            "SET @criou_mod = ROW_COUNT();",
            "SET @id_mod = IF(@criou_mod=1, LAST_INSERT_ID(), NULL);",
            "UPDATE ex_modelo SET HIS_ID_INI=@id_mod WHERE ID_MOD=@id_mod AND @id_mod IS NOT NULL;",
            "",
        ])
    sql.extend([
        "COMMIT;",
        "",
        "SELECT COUNT(*) AS MODELOS_ENFAS_ATIVOS FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_DIRETORIO='ENFAS';",
        "SELECT ID_MOD, NM_MOD, ID_FORMA_DOC, ID_CLASSIFICACAO, ID_NIVEL_ACESSO FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_DIRETORIO='ENFAS' ORDER BY NM_MOD;",
        "",
    ])
    MIGRATION.write_text("\n".join(sql), encoding="utf-8")


if __name__ == "__main__":
    generate()
