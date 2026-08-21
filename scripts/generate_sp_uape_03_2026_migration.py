#!/usr/bin/env python3
"""Generate the MySQL/Flyway load for Portaria UAPE 03/2026.

The source PDF is the 204-page publication in the DOE/SP.  Its Annex III
contains the classification code, retention periods and final destination.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pdfplumber


SERIES_RE = re.compile(r"00[1-7](?:\.\d{2}){2}\.\d{3}")
ACTIVITY_RE = re.compile(r"((?:00[1-7])(?:\.\d{2}){2})\s+(.+)", re.S)
HEADER_RE = re.compile(
    r"(?m)^(00[1-7](?:\.\d{2})?)\s+([^\n]+?)(?:\s+\((?:FUNÇÃO|SUBFUNÇÃO)\))?$"
)


def clean(value: str | None) -> str:
    return " ".join((value or "").replace("–", "-").split()).strip()


def sql(value: str | None) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def period(value: str) -> str | None:
    value = clean(value)
    if not value or value == "-":
        return None
    if value.isdigit():
        return f"{value} ano" if value == "1" else f"{value} anos"
    return value[0].upper() + value[1:]


def extract(pdf_path: Path):
    classifications: dict[str, str] = {}
    schedules: dict[str, tuple[str, str | None, str | None, int | None, str]] = {}

    with pdfplumber.open(pdf_path) as pdf:
        # Annex III occupies PDF pages 108 through 188 (1-based).
        for page in pdf.pages[107:188]:
            text = page.extract_text() or ""
            for code, description in HEADER_RE.findall(text):
                classifications[code] = clean(description)

            for table in page.extract_tables():
                for row in table:
                    if len(row) < 7:
                        continue
                    activity = row[0]

                    if activity:
                        match = ACTIVITY_RE.match(clean(activity))
                        if match:
                            classifications[match.group(1)] = clean(match.group(2))

                    code_index = next(
                        (index for index, value in enumerate(row) if SERIES_RE.fullmatch(clean(value))),
                        None,
                    )
                    if code_index is None:
                        continue

                    code = clean(row[code_index])
                    # PDFium emits a few grid variants. These positions are the
                    # seven visual columns starting at the classification code.
                    positions = {
                        7: [0, 1, 2, 3, 4, 5, 6],
                        8: [1, 2, 3, 4, 5, 6, 7],
                        9: [1, 2, 3, 4, 5, 6, 7],
                        10: [1, 2, 5, 6, 7, 8, 9],
                        11: [1, 2, 5, 6, 7, 8, 9],
                        21: [1, 4, 7, 10, 13, 16, 19],
                    }.get(len(row))
                    if positions is None:
                        continue
                    _, description, current, intermediate, elimination, permanent, note = [
                        clean(row[index]) for index in positions
                    ]
                    if not description:
                        continue

                    description = clean(description)
                    classifications[code] = description
                    destination = 1 if clean(elimination) else (2 if clean(permanent) else None)
                    schedules[code] = (
                        description,
                        period(clean(current)),
                        period(clean(intermediate)),
                        destination,
                        clean(note),
                    )

    # In three rows PDFium shifts the permanent-destination check mark into
    # the observations cell. Preserve the visual meaning of the official table.
    for code in ("001.03.01.002", "001.03.01.003", "002.02.01.001"):
        description, current, intermediate, _, note = schedules[code]
        if note == "✓":
            schedules[code] = (description, current, intermediate, 2, "")

    # "007.00 - Não há" é apenas uma indicação de ausência de subfunção.
    # Mantê-la como classificação colidiria com a função 007 após o padding.
    classifications.pop("007.00", None)

    return classifications, schedules


def render(classifications, schedules) -> str:
    periods = sorted(
        {p for _, current, intermediate, _, _ in schedules.values() for p in (current, intermediate) if p},
        key=str.casefold,
    )

    out = [
        "-- Plano de Classificacao e Tabela de Temporalidade - Portaria UAPE 03/2026 (SP)",
        "-- Fonte: DOE/SP, edicao de 22/05/2026. Carga idempotente para bases existentes.",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_classificacao (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY,",
        "  descricao VARCHAR(4000) NOT NULL",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "",
        "INSERT INTO tmp_sp_classificacao (codificacao, descricao) VALUES",
    ]
    values = [f"({sql(code)}, {sql(desc)})" for code, desc in sorted(classifications.items())]
    out.append(",\n".join(values) + ";")
    out += [
        "",
        "-- O SIGA representa níveis superiores preenchendo os níveis inferiores com zeros.",
        "UPDATE tmp_sp_classificacao SET codificacao=CONCAT(codificacao, '.000')",
        "WHERE codificacao REGEXP '^00[1-7](\\\\.[0-9]{2}){2}
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "UPDATE tmp_sp_classificacao SET codificacao=CONCAT(codificacao, '.00.000')",
        "WHERE codificacao REGEXP '^00[1-7]\\\\.[0-9]{2}
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "UPDATE tmp_sp_classificacao SET codificacao=CONCAT(codificacao, '.00.00.000')",
        "WHERE codificacao REGEXP '^00[1-7]
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "",
        "-- Normaliza também uma carga anterior desta migration, preservando os IDs.",
        "UPDATE ex_classificacao SET codificacao=CONCAT(codificacao, '.000')",
        "WHERE HIS_ATIVO=1 AND OBS='Portaria UAPE 03/2026' AND codificacao REGEXP '^00[1-7](\\\\.[0-9]{2}){2}
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "UPDATE ex_classificacao SET codificacao=CONCAT(codificacao, '.00.000')",
        "WHERE HIS_ATIVO=1 AND OBS='Portaria UAPE 03/2026' AND codificacao REGEXP '^00[1-7]\\\\.[0-9]{2}
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "UPDATE ex_classificacao SET codificacao=CONCAT(codificacao, '.00.00.000')",
        "WHERE HIS_ATIVO=1 AND OBS='Portaria UAPE 03/2026' AND codificacao REGEXP '^00[1-7]
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
;",
        "",
        "UPDATE ex_classificacao c",
        "JOIN tmp_sp_classificacao s ON s.codificacao = c.codificacao",
        "SET c.DESCR_CLASSIFICACAO = s.descricao, c.HIS_ATIVO = 1, c.HIS_DT_FIM = NULL;",
        "",
        "INSERT INTO ex_classificacao",
        "  (codificacao, DESCR_CLASSIFICACAO, OBS, HIS_ATIVO, HIS_DT_INI)",
        "SELECT s.codificacao, s.descricao, 'Portaria UAPE 03/2026', 1, CURRENT_TIMESTAMP",
        "FROM tmp_sp_classificacao s",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_classificacao c WHERE c.codificacao = s.codificacao);",
        "",
        "UPDATE ex_classificacao",
        "SET HIS_ID_INI = ID_CLASSIFICACAO",
        "WHERE HIS_ID_INI IS NULL AND codificacao IN (SELECT codificacao FROM tmp_sp_classificacao);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_periodo (descricao VARCHAR(128) NOT NULL PRIMARY KEY);",
        "INSERT INTO tmp_sp_periodo (descricao) VALUES",
        ",\n".join(f"({sql(p)})" for p in periods) + ";",
        "",
        "INSERT INTO ex_temporalidade",
        "  (DESC_TEMPORALIDADE, VALOR_TEMPORALIDADE, ID_UNIDADE_MEDIDA, HIS_ATIVO)",
        "SELECT p.descricao,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN CAST(SUBSTRING_INDEX(p.descricao, ' ', 1) AS UNSIGNED) END,",
        "       CASE WHEN p.descricao REGEXP '^[0-9]+ anos?$' THEN 1 END, 1",
        "FROM tmp_sp_periodo p",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_temporalidade t WHERE LOWER(t.DESC_TEMPORALIDADE)=LOWER(p.descricao));",
        "",
        "UPDATE ex_temporalidade SET HIS_ID_INI = ID_TEMPORALIDADE",
        "WHERE HIS_ID_INI IS NULL AND DESC_TEMPORALIDADE IN (SELECT descricao FROM tmp_sp_periodo);",
        "",
        "CREATE TEMPORARY TABLE tmp_sp_via (",
        "  codificacao VARCHAR(13) NOT NULL PRIMARY KEY, corrente VARCHAR(128),",
        "  intermediaria VARCHAR(128), destinacao_final TINYINT, observacao VARCHAR(4000)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;",
        "INSERT INTO tmp_sp_via VALUES",
    ]
    via_values = []
    for code, (_, current, intermediate, destination, note) in sorted(schedules.items()):
        via_values.append(f"({sql(code)}, {sql(current)}, {sql(intermediate)}, {destination or 'NULL'}, {sql(note)})")
    out.append(",\n".join(via_values) + ";")
    out += [
        "",
        "UPDATE ex_via v",
        "JOIN ex_classificacao c ON c.ID_CLASSIFICACAO=v.ID_CLASSIFICACAO AND c.HIS_ATIVO=1",
        "JOIN tmp_sp_via s ON s.codificacao=c.codificacao AND v.COD_VIA='1'",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "SET v.ID_TEMPORAL_ARQ_COR=tc.ID_TEMPORALIDADE, v.ID_TEMPORAL_ARQ_INT=ti.ID_TEMPORALIDADE,",
        "    v.ID_DESTINACAO_FINAL=s.destinacao_final, v.OBS=s.observacao, v.HIS_ATIVO=1, v.HIS_DT_FIM=NULL;",
        "",
        "INSERT INTO ex_via",
        "  (ID_CLASSIFICACAO, ID_DESTINACAO, COD_VIA, ID_TEMPORAL_ARQ_COR, ID_TEMPORAL_ARQ_INT,",
        "   OBS, ID_DESTINACAO_FINAL, HIS_DT_INI, HIS_ATIVO)",
        "SELECT c.ID_CLASSIFICACAO, 58, '1', tc.ID_TEMPORALIDADE, ti.ID_TEMPORALIDADE,",
        "       s.observacao, s.destinacao_final, CURRENT_TIMESTAMP, 1",
        "FROM tmp_sp_via s",
        "JOIN ex_classificacao c ON c.codificacao=s.codificacao AND c.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade tc ON LOWER(tc.DESC_TEMPORALIDADE)=LOWER(s.corrente) AND tc.HIS_ATIVO=1",
        "LEFT JOIN ex_temporalidade ti ON LOWER(ti.DESC_TEMPORALIDADE)=LOWER(s.intermediaria) AND ti.HIS_ATIVO=1",
        "WHERE NOT EXISTS (SELECT 1 FROM ex_via v WHERE v.ID_CLASSIFICACAO=c.ID_CLASSIFICACAO AND v.COD_VIA='1');",
        "",
        "UPDATE ex_via SET HIS_ID_INI=ID_VIA",
        "WHERE HIS_ID_INI IS NULL AND ID_CLASSIFICACAO IN",
        "  (SELECT c.ID_CLASSIFICACAO FROM ex_classificacao c JOIN tmp_sp_via s ON s.codificacao=c.codificacao);",
        "",
        "DROP TEMPORARY TABLE tmp_sp_via;",
        "DROP TEMPORARY TABLE tmp_sp_periodo;",
        "DROP TEMPORARY TABLE tmp_sp_classificacao;",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    classifications, schedules = extract(args.pdf)
    if len(schedules) < 700:
        raise SystemExit(f"Extraction incomplete: only {len(schedules)} series")
    args.output.write_text(render(classifications, schedules), encoding="utf-8")
    print(f"generated {len(classifications)} classifications and {len(schedules)} schedules")


if __name__ == "__main__":
    main()
