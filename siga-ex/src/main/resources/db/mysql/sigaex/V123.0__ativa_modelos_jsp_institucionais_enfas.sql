-- Ativa o núcleo institucional ENFAS em JSP.
-- Mantém os arquivos Freemarker das versões anteriores no banco para rastreabilidade/rollback,
-- mas passa a usar JSPs versionados no WAR como fonte ativa dos modelos essenciais.
START TRANSACTION;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Ofício' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasOficio.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Memorando' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasMemorando.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Despacho' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasDespacho.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Informação' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasInformacao.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Parecer' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasParecer.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Contrato' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasContrato.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Folha Inicial' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasFolhaInicial.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

SET @id_mod = (SELECT ID_MOD FROM ex_modelo WHERE HIS_ATIVO=1 AND NM_MOD='Processo Administrativo' ORDER BY ID_MOD DESC LIMIT 1);
UPDATE ex_modelo SET ID_ARQ=NULL, NM_ARQ_MOD='enfasProcessoAdministrativo.jsp', NM_DIRETORIO=NULL, DESC_MOD='Modelo institucional ENFAS - JSP' WHERE ID_MOD=@id_mod;

COMMIT;
