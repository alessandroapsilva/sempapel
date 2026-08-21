#!/usr/bin/env python3
"""Gera modelos essenciais ENFAS e a migration de atualização V121."""

from __future__ import annotations

import hashlib
import importlib.util
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_GENERATOR = ROOT / "scripts/generate_enfas_freemarker_models.py"
MODEL_DIR = ROOT / "siga-ex/src/main/resources/modelos/enfas"
MIGRATION = ROOT / "siga-ex/src/main/resources/db/mysql/sigaex/V121.0__atualiza_modelos_essenciais_enfas.sql"

spec = importlib.util.spec_from_file_location("enfas_base_models", BASE_GENERATOR)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)


def model(name: str, form: str, label: str, classification: str | None, fields: str, html: str) -> dict:
    return {
        "name": name,
        "form": form,
        "classification": classification,
        "content": base.template(name, base.common_interview(fields), base.common_document(label, html)),
    }


MODELS = [
    model("Ofício", "Ofício", "OFÍCIO", "006.01.10.001", '''[@grupo titulo="Destinatário"]
    [@grupo][@texto titulo="Nome" var="destinatarioNome" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="Cargo/Função" var="destinatarioCargo" largura="35" maxcaracteres="100"/][/@grupo]
    [@grupo][@texto titulo="Empresa ou órgão" var="destinatarioOrganizacao" largura="60" maxcaracteres="150"/][@texto titulo="Cidade/UF" var="destinatarioCidade" largura="25" maxcaracteres="80"/][/@grupo]
    [@grupo][@texto titulo="Vocativo" var="vocativo" largura="45" maxcaracteres="100"/][@selecao titulo="Fecho" var="fecho" opcoes="Atenciosamente;Respeitosamente;Cordialmente"/][/@grupo]
[/@grupo]''', '''<p>${vocativo!"Prezado(a) Senhor(a)"},</p><p><strong>${destinatarioNome!}</strong>[#if (destinatarioCargo!"") != ""]<br/>${destinatarioCargo!}[/#if][#if (destinatarioOrganizacao!"") != ""]<br/>${destinatarioOrganizacao!}[/#if][#if (destinatarioCidade!"") != ""]<br/>${destinatarioCidade!}[/#if]</p><p>${fecho!"Atenciosamente"},</p>'''),
    model("Memorando", "Memorando", "MEMORANDO", "006.01.10.001", '''[@grupo titulo="Encaminhamento interno"]
    [@grupo][@lotacao titulo="Unidade destinatária" var="unidadeDestinataria" obrigatorio=true/][/@grupo]
    [@grupo][@texto titulo="Aos cuidados de" var="aosCuidados" largura="55" maxcaracteres="150"/][@selecao titulo="Prioridade" var="prioridade" opcoes="Normal;Alta;Urgente"/][/@grupo]
[/@grupo]''', '''<p><strong>DE:</strong> ${doc.titular.lotacao.descricao!}</p><p><strong>PARA:</strong> ${unidadeDestinataria!}</p>[#if (aosCuidados!"") != ""]<p><strong>A/C:</strong> ${aosCuidados!}</p>[/#if]<p><strong>Prioridade:</strong> ${prioridade!"Normal"}</p>'''),
    model("Despacho", "Despacho", "DESPACHO", "006.01.09.002", '''[@grupo titulo="Encaminhamento"]
    [@grupo][@texto titulo="Documento de referência" var="documentoReferencia" largura="45" maxcaracteres="100"/][@lotacao titulo="Unidade de destino" var="unidadeDestino"/][/@grupo]
    [@grupo][@selecao titulo="Decisão" var="decisao" opcoes="Ciente;De acordo;Deferido;Indeferido;Para providências;Para análise" obrigatorio="Sim"/][/@grupo]
[/@grupo]''', '''[#if (documentoReferencia!"") != ""]<p><strong>Referência:</strong> ${documentoReferencia!}</p>[/#if][#if (unidadeDestino!"") != ""]<p><strong>Destino:</strong> ${unidadeDestino!}</p>[/#if]<p><strong>Decisão:</strong> ${decisao!}</p>'''),
    model("Informação", "Informação", "INFORMAÇÃO", "006.01.09.002", '''[@grupo titulo="Análise"]
    [@grupo][@texto titulo="Documento de referência" var="documentoReferencia" largura="55" maxcaracteres="120"/][@texto titulo="Unidade demandante" var="unidadeDemandante" largura="35" maxcaracteres="100"/][/@grupo]
    [@memo titulo="Conclusão" var="conclusao" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]''', '''[#if (documentoReferencia!"") != ""]<p><strong>Referência:</strong> ${documentoReferencia!}</p>[/#if][#if (unidadeDemandante!"") != ""]<p><strong>Unidade demandante:</strong> ${unidadeDemandante!}</p>[/#if]<p><strong>Conclusão:</strong><br/>${conclusao!}</p>'''),
    model("Parecer", "Parecer", "PARECER", "006.01.09.002", '''[@grupo titulo="Parecer"]
    [@grupo][@texto titulo="Solicitante" var="solicitante" largura="50" maxcaracteres="150"/][@texto titulo="Referência" var="documentoReferencia" largura="35" maxcaracteres="100"/][/@grupo]
    [@memo titulo="Fundamentação" var="fundamentacao" colunas="90" linhas="5" obrigatorio=true/]
    [@memo titulo="Conclusão do parecer" var="conclusao" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]''', '''[#if (solicitante!"") != ""]<p><strong>Solicitante:</strong> ${solicitante!}</p>[/#if][#if (documentoReferencia!"") != ""]<p><strong>Referência:</strong> ${documentoReferencia!}</p>[/#if]<p><strong>Fundamentação:</strong><br/>${fundamentacao!}</p><p><strong>Conclusão:</strong><br/>${conclusao!}</p>'''),
    model("Contrato", "Contrato", "CONTRATO", "004.01.04.002", '''[@grupo titulo="Partes e vigência"]
    [@grupo][@texto titulo="Contratada" var="contratada" largura="55" maxcaracteres="150" obrigatorio="Sim"/][@texto titulo="CNPJ/CPF" var="documentoContratada" largura="25" maxcaracteres="24" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Objeto" var="objetoContrato" largura="80" maxcaracteres="220" obrigatorio="Sim"/][/@grupo]
    [@grupo][@texto titulo="Valor" var="valorContrato" largura="22" maxcaracteres="30" obrigatorio="Sim"/][@data titulo="Início da vigência" var="vigenciaInicio" obrigatorio=true/][@data titulo="Fim da vigência" var="vigenciaFim" obrigatorio=true/][/@grupo]
[/@grupo]''', '''<p><strong>Contratada:</strong> ${contratada!} — ${documentoContratada!}</p><p><strong>Objeto:</strong> ${objetoContrato!}</p><p><strong>Valor:</strong> ${valorContrato!}</p><p><strong>Vigência:</strong> ${vigenciaInicio!} a ${vigenciaFim!}</p>'''),
    model("Folha Inicial", "Formulário", "FOLHA INICIAL", None, '''[@grupo titulo="Identificação do processo"]
    [@grupo][@texto titulo="Número do processo" var="numeroProcesso" largura="35" maxcaracteres="60"/][@data titulo="Data de abertura" var="dataAbertura" obrigatorio=true/][/@grupo]
    [@grupo][@texto titulo="Unidade responsável" var="unidadeResponsavel" largura="60" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Objeto do processo" var="objetoProcesso" colunas="90" linhas="4" obrigatorio=true/]
[/@grupo]''', '''<div style="border:1px solid #333;padding:16px"><p><strong>Processo:</strong> ${numeroProcesso!(doc.codigo!'')}</p><p><strong>Abertura:</strong> ${dataAbertura!}</p><p><strong>Unidade responsável:</strong> ${unidadeResponsavel!}</p><p><strong>Objeto:</strong><br/>${objetoProcesso!}</p></div>'''),
    model("Processo Administrativo", "Processo Administrativo", "PROCESSO ADMINISTRATIVO", None, '''[@grupo titulo="Abertura do processo"]
    [@grupo][@selecao titulo="Área" var="areaProcesso" opcoes="Administrativo;Compras e contratos;Financeiro;Recursos humanos;Patrimônio;Tecnologia;Proteção de dados;Qualidade" obrigatorio="Sim"/][@texto titulo="Unidade responsável" var="unidadeResponsavel" largura="45" maxcaracteres="150" obrigatorio="Sim"/][/@grupo]
    [@memo titulo="Objeto do processo" var="objetoProcesso" colunas="90" linhas="4" obrigatorio=true/]
    [@texto titulo="Interessado principal" var="interessadoPrincipal" largura="60" maxcaracteres="150"/]
[/@grupo]''', '''<div style="border:2px solid #333;padding:18px"><p><strong>Número:</strong> ${doc.codigo!}</p><p><strong>Data de abertura:</strong> ${doc.dtDocDDMMYYYY!}</p><p><strong>Área:</strong> ${areaProcesso!}</p><p><strong>Unidade responsável:</strong> ${unidadeResponsavel!}</p>[#if (interessadoPrincipal!"") != ""]<p><strong>Interessado:</strong> ${interessadoPrincipal!}</p>[/#if]<p><strong>Objeto:</strong><br/>${objetoProcesso!}</p></div>'''),
]


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def generate() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    sql = [
        "-- Atualização dos modelos essenciais da Enfermagem Alessandro Silva.",
        "-- Substitui modelos públicos legados por versões empresariais Freemarker.",
        "-- Requer V119 e pode ser executada novamente com segurança.",
        "START TRANSACTION;",
        "",
    ]
    for entry in MODELS:
        slug = unicodedata.normalize("NFKD", entry["name"].lower()).encode("ascii", "ignore").decode("ascii").replace(" ", "_")
        filename = f"{slug}.ftl"
        content = entry["content"].strip() + "\n"
        (MODEL_DIR / filename).write_text(content, encoding="utf-8")
        payload = content.encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        classification = "NULL" if entry["classification"] is None else f"(SELECT ID_CLASSIFICACAO FROM ex_classificacao WHERE HIS_ATIVO=1 AND codificacao={quote(entry['classification'])} LIMIT 1)"
        sql.extend([
            f"-- {entry['name']}",
            f"SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD={quote(entry['name'])} ORDER BY ID_MOD DESC LIMIT 1);",
            "SET @id_arq = (SELECT m.ID_ARQ FROM ex_modelo m JOIN corporativo.cp_arquivo a ON a.ID_ARQ=m.ID_ARQ "
            f"WHERE m.ID_MOD=@id_mod AND m.NM_DIRETORIO='ENFAS' AND a.HASH_SHA256='{digest}' LIMIT 1);",
            "INSERT INTO corporativo.cp_arquivo (ID_ORGAO_USU, CONTEUDO_TP_ARQ, TP_ARMAZENAMENTO, CAMINHO, TAMANHO_ARQ, HASH_SHA256, NOME_ARQ)",
            f"SELECT NULL, 'template/freemarker', 'TABELA', NULL, {len(payload)}, '{digest}', {quote(filename)} WHERE @id_arq IS NULL;",
            "SET @novo_arq = IF(ROW_COUNT()=1, LAST_INSERT_ID(), NULL);",
            "SET @id_arq = COALESCE(@id_arq, @novo_arq);",
            "UPDATE corporativo.cp_arquivo SET CONTEUDO_TP_ARQ='template/freemarker', TP_ARMAZENAMENTO='TABELA', CAMINHO=NULL, "
            f"TAMANHO_ARQ={len(payload)}, HASH_SHA256='{digest}', NOME_ARQ={quote(filename)} WHERE ID_ARQ=@id_arq;",
            "INSERT INTO corporativo.cp_arquivo_blob (ID_ARQ_BLOB, CONTEUDO_ARQ_BLOB)",
            f"VALUES (@id_arq, UNHEX('{payload.hex()}')) ON DUPLICATE KEY UPDATE CONTEUDO_ARQ_BLOB=VALUES(CONTEUDO_ARQ_BLOB);",
            "INSERT INTO ex_modelo (NM_MOD, DESC_MOD, ID_ARQ, CONTEUDO_TP_BLOB, NM_ARQ_MOD, ID_CLASSIFICACAO, ID_FORMA_DOC, ID_NIVEL_ACESSO, HIS_ID_INI, HIS_DT_INI, HIS_ATIVO, NM_DIRETORIO)",
            f"SELECT {quote(entry['name'])}, 'Modelo empresarial - Enfermagem Alessandro Silva', @id_arq, 'template/freemarker', NULL, {classification}, f.ID_FORMA_DOC, 1, NULL, CURRENT_TIMESTAMP, 1, 'ENFAS' FROM ex_forma_documento f",
            f"WHERE f.DESCR_FORMA_DOC={quote(entry['form'])} AND @id_mod IS NULL LIMIT 1;",
            "SET @novo_mod = IF(ROW_COUNT()=1, LAST_INSERT_ID(), NULL);",
            "SET @id_mod = COALESCE(@id_mod, @novo_mod);",
            "UPDATE ex_modelo SET ID_ARQ=@id_arq, CONTEUDO_BLOB_MOD=NULL, CONTEUDO_TP_BLOB='template/freemarker', NM_ARQ_MOD=NULL, "
            f"ID_CLASSIFICACAO={classification}, ID_NIVEL_ACESSO=1, NM_DIRETORIO='ENFAS', DESC_MOD='Modelo empresarial - Enfermagem Alessandro Silva', HIS_ID_INI=COALESCE(HIS_ID_INI, @id_mod) WHERE ID_MOD=@id_mod;",
            "",
        ])
    sql.extend([
        "COMMIT;",
        "SELECT ID_MOD, NM_MOD, CONTEUDO_TP_BLOB, ID_FORMA_DOC, ID_CLASSIFICACAO, ID_NIVEL_ACESSO, HIS_ATIVO",
        "FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD IN ('Ofício','Memorando','Despacho','Informação','Parecer','Contrato','Folha Inicial','Processo Administrativo') ORDER BY NM_MOD;",
        "",
    ])
    MIGRATION.write_text("\n".join(sql), encoding="utf-8")


if __name__ == "__main__":
    generate()
