from pathlib import Path
import re

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
s = jsp.read_text(encoding='utf-8')

repls = [
    (r'<button id="btnGravar"[^>]*>\s*<i class="fas fa-save"></i>\s*<u>G</u>ravar\s*</button>',
     '<button id="btnGravar" type="button" onclick="javascript: gravarDoc(); return false;" name="gravar" class="btn btn-primary" accesskey="g" title="Apenas grava o documento podendo continuar a Edição"><u>G</u>ravar</button>'),
    (r'<button id="btnFinalizarAssinar"[^>]*>\s*<i class="fas fa-check-circle"></i>\s*<u>F</u>inalizar e Assinar\s*</button>',
     '<button id="btnFinalizarAssinar" type="button" onclick="javascript: gravarAssinarDoc(); return false;" name="finalizareGravar" class="btn btn-primary" accesskey="f" title="Finalizar documento em definitivo e em seguida realizar assinatura digital"><u>F</u>inalizar e Assinar</button>'),
    (r'<button type="button" name="ver_doc"[^>]*>\s*<i class="fas fa-file-alt"></i>\s*<u>V</u>er Documento\s*</button>',
     '<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info" accesskey="v" title="Visualizar o documento gerado"><u>V</u>er Documento</button>'),
    (r'<button type="button" name="ver_doc_pdf"[^>]*>\s*<i class="fas fa-print"></i>\s*Ver <u>I</u>mpressão\s*</button>',
     '<button type="button" name="ver_doc_pdf" onclick="javascript: popitup_documento(true); return false;" class="btn btn-info" accesskey="i" title="Visualizar versão para impressão (PDF)">Ver <u>I</u>mpressão</button>'),
    (r'<button type="button" name="voltar"[^>]*>\s*<i class="fas fa-arrow-left"></i>\s*Volta<u>r</u>\s*</button>',
     '<button type="button" name="voltar" onclick="javascript: history.back();" class="btn btn-info" accesskey="r" title="Voltar à página anterior">Volta<u>r</u></button>'),
]

for pattern, replacement in repls:
    s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError('Botão esperado não encontrado: ' + pattern[:60])
    s = s2
jsp.write_text(s, encoding='utf-8')

js = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
v = js.read_text(encoding='utf-8')

inicio = v.index('function exibirModalCamposObrigatoriosDocumento(mensagens, finalizar) {')
fim = v.index('\n\nfunction validarCamposObrigatoriosEditaDocumento()', inicio)

novo = r'''function obterCampoObrigatorioPrioritarioDocumento(mensagens) {
	function vazio(nome) {
		var el = $('[name="' + nome + '"]').first();
		if (el.length == 0 || !campoDeveAparecerNoResumoDocumento(el)) return false;
		return !String(el.val() || '').trim();
	}

	function selecaoVazia(nomeSigla) {
		var sigla = $('[name="' + nomeSigla + '"]').first();
		if (sigla.length == 0 || !campoDeveAparecerNoResumoDocumento(sigla)) return false;
		var id = $('[name="' + nomeSigla.replace('Sel.sigla', 'Sel.id') + '"]').first();
		return !String((id.length ? id.val() : sigla.val()) || '').trim();
	}

	if (vazio('exDocumentoDTO.descrDocumento')) return 'Assunto';

	var tipo = $('[name="exDocumentoDTO.tipoDestinatario"]').val();
	if (tipo == '1' && selecaoVazia('exDocumentoDTO.destinatarioSel.sigla')) return 'Destinatário - Usuário';
	if (tipo == '2' && selecaoVazia('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) return 'Destinatário - Lotação';
	if (tipo == '3' && selecaoVazia('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) return 'Destinatário - Órgão Externo';
	if (tipo && tipo != '1' && tipo != '2' && tipo != '3' && vazio('exDocumentoDTO.nmDestinatario')) return 'Destinatário - Campo Livre';

	if (selecaoVazia('exDocumentoDTO.subscritorSel.sigla')) return 'Responsável pela Assinatura';
	if ($('#substitutoSwitch').is(':checked') && selecaoVazia('exDocumentoDTO.titularSel.sigla')) return 'Substituto Responsável pela Assinatura';
	if (selecaoVazia('exDocumentoDTO.classificacaoSel.sigla')) return 'Tipo Documental';

	if (mensagens && mensagens.length) {
		var m = String(mensagens[0] || '')
			.replace(/^Favor\s+(preencher|informar|selecionar)\s+(o\s+|a\s+)?campo\s*/i, '')
			.replace(/^Preencha\s+(o\s+|a\s+)?campo\s*/i, '')
			.replace(/[.'"]+$/g, '').trim();
		if (m) return m;
	}
	return 'Campo obrigatório';
}

function exibirModalCamposObrigatoriosDocumento(mensagens, finalizar) {
	var elemento = obterPrimeiroCampoInvalidoDocumento();
	var nomeCampo = obterCampoObrigatorioPrioritarioDocumento(mensagens);
	var msg = "Preencha o campo '" + nomeCampo + "' antes de gravar o documento.";

	if (typeof sigaModal !== 'undefined' && typeof sigaModal.alerta === 'function') {
		var modal = sigaModal.alerta(msg);
		if (modal && typeof modal.focus === 'function') modal.focus(elemento);
	} else {
		alert(msg);
		if (elemento && typeof elemento.focus === 'function') elemento.focus();
	}
}'''

v = v[:inicio] + novo + v[fim:]
v = v.replace("'Favor preencher o campo responsável pela assinatura'", "'Responsável pela Assinatura'")
v = v.replace("'Favor preencher o campo substituto do responsável pela assinatura'", "'Substituto Responsável pela Assinatura'")
v = v.replace("'Favor preencher o campo classificação documental'", "'Tipo Documental'")
v = v.replace("'Favor preencher o campo assunto'", "'Assunto'")
js.write_text(v, encoding='utf-8')
