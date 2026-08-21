-- Catálogo de espécies documentais administrativas da Enfermagem Alessandro Silva.
-- Não cria modelos e não altera o plano de classificação.
-- A carga é idempotente por descrição e sigla.

DROP TEMPORARY TABLE IF EXISTS tmp_enfas_especie;

CREATE TEMPORARY TABLE tmp_enfas_especie (
    DESCRICAO VARCHAR(64) NOT NULL,
    SIGLA VARCHAR(3) NOT NULL,
    ID_TIPO_FORMA_DOC INT UNSIGNED NOT NULL DEFAULT 1,
    ID_TP_DOC INT UNSIGNED NOT NULL,
    PRIMARY KEY (SIGLA, ID_TP_DOC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Comunicação, governança e qualidade (origem: Interno Produzido).
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Carta', 'CAR', 1),
('Moção', 'MOC', 1),
('Voto', 'VOT', 1),
('Abaixo-assinado', 'ABA', 1),
('Circular', 'CIR', 1),
('Aviso', 'AVI', 1),
('Comunicado', 'COM', 1),
('Comunicação Interna', 'CMI', 1),
('Ata', 'ATA', 1),
('Pauta de Reunião', 'PAU', 1),
('Convocação', 'COV', 1),
('Declaração', 'DEC', 1),
('Autorização', 'AUT', 1),
('Edital', 'EDT', 1),
('Notificação', 'NOT', 1),
('Ordem de Serviço', 'ODS', 1),
('Nota Técnica', 'NTC', 1),
('Instrução Normativa', 'INM', 1),
('Política Interna', 'POL', 1),
('Regulamento', 'REG', 1),
('Regimento', 'RGT', 1),
('Resolução', 'RES', 1),
('Deliberação', 'DEL', 1),
('Portaria', 'PRT', 1),
('Manual', 'MAN', 1),
('Procedimento Operacional Padrão', 'POP', 1),
('Instrução de Trabalho', 'ITR', 1),
('Plano de Trabalho', 'PLT', 1),
('Termo', 'TER', 1),
('Termo de Referência', 'TDR', 1),
('Termo de Abertura', 'TAB', 1),
('Termo de Encerramento', 'TEN', 1);

-- Compras, fornecedores e contratos.
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Solicitação de Compra', 'SDC', 1),
('Requisição de Material', 'RQM', 1),
('Cotação de Preços', 'COT', 1),
('Cotação de Preços', 'COT', 4),
('Mapa Comparativo de Preços', 'MCP', 1),
('Proposta Comercial', 'PPC', 1),
('Proposta Comercial', 'PPC', 4),
('Autorização de Compra', 'ADC', 1),
('Pedido de Compra', 'PDC', 1),
('Ordem de Compra', 'ODC', 1),
('Aditivo Contratual', 'ADI', 1),
('Atestado de Recebimento', 'ATR', 1),
('Cadastro de Fornecedor', 'CDF', 1),
('Avaliação de Fornecedor', 'AVF', 1),
('Relatório de Fiscalização Contratual', 'RFC', 1),
('Notificação ao Fornecedor', 'NFR', 1),
('Termo de Rescisão Contratual', 'TRC', 1);

-- Financeiro e contabilidade.
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Nota Fiscal', 'NFS', 4),
('Recibo', 'REC', 1),
('Recibo', 'REC', 4),
('Comprovante de Pagamento', 'CPG', 4),
('Boleto', 'BOL', 4),
('Extrato Bancário', 'EXB', 4),
('Fluxo de Caixa', 'FLC', 1),
('Conciliação Bancária', 'CCB', 1),
('Contas a Pagar', 'CTP', 1),
('Contas a Receber', 'CTR', 1),
('Solicitação de Reembolso', 'SRE', 1),
('Solicitação de Adiantamento', 'SAD', 1),
('Prestação de Contas', 'PTC', 1),
('Relatório Financeiro', 'RFI', 1),
('Aviso de Cobrança', 'ACB', 1),
('Nota de Crédito', 'NCR', 1),
('Guia de Recolhimento', 'GRC', 4);

-- Recursos humanos e administração de pessoal.
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Ficha de Admissão', 'FAD', 1),
('Ficha de Registro de Empregado', 'FRE', 1),
('Formulário de Alteração Cadastral', 'FAC', 1),
('Solicitação de Férias', 'SFE', 1),
('Aviso de Férias', 'AVE', 1),
('Folha de Ponto', 'FPT', 1),
('Autorização de Hora Extra', 'AHE', 1),
('Avaliação de Desempenho', 'AVD', 1),
('Advertência', 'ADV', 1),
('Termo de Suspensão', 'TSU', 1),
('Aviso de Desligamento', 'ADL', 1),
('Termo de Desligamento', 'TDL', 1),
('Lista de Presença', 'LPR', 1),
('Termo de Confidencialidade', 'TCF', 1),
('Termo de Entrega de Equipamento', 'TEE', 1),
('Certificado de Treinamento', 'CTE', 4),
('Atestado de Saúde Ocupacional', 'ASO', 4);

-- Patrimônio, estoque e manutenção.
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Ficha de Bem Patrimonial', 'FBP', 1),
('Termo de Responsabilidade Patrimonial', 'TRP', 1),
('Termo de Transferência de Bem', 'TTB', 1),
('Inventário Patrimonial', 'INP', 1),
('Termo de Baixa Patrimonial', 'TBP', 1),
('Entrada de Material', 'ENM', 1),
('Saída de Material', 'SAM', 1),
('Inventário de Estoque', 'INE', 1),
('Ordem de Manutenção', 'ODM', 1),
('Relatório de Manutenção', 'RMA', 1),
('Certificado de Garantia', 'CGA', 4);

-- Tecnologia, proteção de dados, segurança e auditoria.
INSERT INTO tmp_enfas_especie (DESCRICAO, SIGLA, ID_TP_DOC) VALUES
('Solicitação de Acesso a Sistema', 'SAS', 1),
('Autorização de Acesso a Sistema', 'AAS', 1),
('Revogação de Acesso a Sistema', 'RAS', 1),
('Registro de Incidente', 'RIN', 1),
('Relatório de Incidente', 'RDI', 1),
('Solicitação do Titular de Dados', 'STD', 1),
('Termo de Eliminação de Dados', 'TED', 1),
('Relatório de Auditoria', 'RAU', 1),
('Relatório de Backup', 'RBP', 1),
('Registro de Mudança', 'RGM', 1);

-- Falha explicitamente se o catálogo proposto reutilizar uma sigla para
-- descrições diferentes. Uma espécie pode ter mais de uma origem.
DROP TEMPORARY TABLE IF EXISTS tmp_enfas_conflito;
CREATE TEMPORARY TABLE tmp_enfas_conflito AS
SELECT SIGLA
FROM tmp_enfas_especie
GROUP BY SIGLA
HAVING COUNT(DISTINCT DESCRICAO) > 1;

-- Insere apenas espécies ainda inexistentes.
INSERT INTO ex_forma_documento (
    DESCR_FORMA_DOC,
    SIGLA_FORMA_DOC,
    ID_TIPO_FORMA_DOC,
    IS_COMPOSTO
)
SELECT DISTINCT
    t.DESCRICAO,
    t.SIGLA,
    t.ID_TIPO_FORMA_DOC,
    NULL
FROM tmp_enfas_especie t
WHERE NOT EXISTS (SELECT 1 FROM tmp_enfas_conflito)
  AND NOT EXISTS (
      SELECT 1
      FROM ex_forma_documento f
      WHERE f.DESCR_FORMA_DOC = t.DESCRICAO
         OR f.SIGLA_FORMA_DOC = t.SIGLA
  );

-- Vincula cada espécie às origens indicadas na tabela temporária.
INSERT INTO ex_tp_forma_doc (ID_FORMA_DOC, ID_TP_DOC)
SELECT
    f.ID_FORMA_DOC,
    t.ID_TP_DOC
FROM tmp_enfas_especie t
JOIN ex_forma_documento f
  ON f.DESCR_FORMA_DOC = t.DESCRICAO
 AND f.SIGLA_FORMA_DOC = t.SIGLA
WHERE NOT EXISTS (SELECT 1 FROM tmp_enfas_conflito)
  AND NOT EXISTS (
      SELECT 1
      FROM ex_tp_forma_doc tf
      WHERE tf.ID_FORMA_DOC = f.ID_FORMA_DOC
        AND tf.ID_TP_DOC = t.ID_TP_DOC
  );

-- Resultado resumido para auditoria da migration.
SELECT
    COUNT(DISTINCT f.ID_FORMA_DOC) AS ESPECIES_CATALOGO,
    COUNT(*) AS VINCULOS_DE_ORIGEM
FROM tmp_enfas_especie t
JOIN ex_forma_documento f
  ON f.DESCR_FORMA_DOC = t.DESCRICAO
 AND f.SIGLA_FORMA_DOC = t.SIGLA
JOIN ex_tp_forma_doc tf
  ON tf.ID_FORMA_DOC = f.ID_FORMA_DOC
 AND tf.ID_TP_DOC = t.ID_TP_DOC;

DROP TEMPORARY TABLE IF EXISTS tmp_enfas_conflito;
DROP TEMPORARY TABLE IF EXISTS tmp_enfas_especie;
