from pathlib import Path
import re

js = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
s = js.read_text(encoding='utf-8')

# 1) Prioridade e nomes explícitos dos campos principais do edita.jsp.
pat = re.compile(r"function obterCampoObrigatorioPrioritarioDocumento\(mensagens\) \{.*?\n\}\n\nfunction exibirModalCamposObrigatoriosDocumento", re.S)
new = r'''function obterCampoObrigatorioPrioritarioDocumento(mensagens) {
	function vazio(nomeSigla) {
		var el = $('[name="' + nomeSigla + '"]').first();
		if (el.length == 0 || !campoDeveAparecerNoResumoDocumento(el)) return false;
		var nomeId = nomeSigla.replace('Sel.sigla', 'Sel.id');
		var id = $('[name="' + nomeId + '"]').first();
		var valor = id.length ? id.val() : el.val();
		return !String(valor || '').trim();
	}

	// PBdoc: Assunto é sempre o primeiro obrigatório apresentado.
	var assunto = $('[name="exDocumentoDTO.descrDocumento"]').first();
	if (assunto.length > 0 && campoDeveAparecerNoResumoDocumento(assunto)
			&& !String(assunto.val() || '').trim()) {
		return 'Assunto';
	}

	// Destinatário: usa também a opção escolhida na tela.
	var tipoDestinatario = String($('[name="exDocumentoDTO.tipoDestinatario"]').val() || '');
	if (tipoDestinatario === '1' && vazio('exDocumentoDTO.destinatarioSel.sigla')) return 'Destinatário - Usuário';
	if (tipoDestinatario === '2' && vazio('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) return 'Destinatário - Lotação';
	if (tipoDestinatario === '3' && vazio('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) return 'Destinatário - Órgão Externo';
	if (tipoDestinatario && !['1','2','3'].includes(tipoDestinatario)) {
		var nmDest = $('[name="exDocumentoDTO.nmDestinatario"]').first();
		if (nmDest.length && !String(nmDest.val() || '').trim()) return 'Destinatário';
	}

	if (vazio('exDocumentoDTO.classificacaoSel.sigla')) return 'Classificação Documental';
	if (vazio('exDocumentoDTO.subscritorSel.sigla')) return 'Responsável pela Assinatura';
	if ($('#substitutoSwitch').is(':checked') && vazio('exDocumentoDTO.titularSel.sigla')) return 'Titular';

	var invalido = $('#frm').find('.is-invalid').filter(function() {
		return campoDeveAparecerNoResumoDocumento($(this));
	}).first();

	if (invalido.length > 0) {
		var div = obterMensagemDivErro(invalido);
		var nomeSalvo = limparNomeCampoDocumento(div.attr('data-nome-campo-documento'));
		if (nomeSalvo) return nomeSalvo;
		var nomeReal = limparNomeCampoDocumento(obterNomeCampoDocumento(invalido));
		if (nomeReal) return nomeReal;
	}

	if (mensagens && mensagens.length) {
		var m = String(mensagens[0] || '')
			.replace(/^Favor\s+(preencher|informar|selecionar|selecione)\s+(o\s+|a\s+)?campo\s*/i, '')
			.replace(/^Preencha\s+(o\s+|a\s+)?campo\s*/i, '')
			.replace(/[.'\"]+$/g, '')
			.trim();
		if (m && !/^um campo obrigatório$/i.test(m) && !/^campo obrigatório$/i.test(m)) return m;
	}

	// Última tentativa: procura o primeiro obrigatório visível e usa o nome real do label.
	var obrigatorios = $('#frm').find('[name=obrigatorios]');
	for (var i = 0; i < obrigatorios.length; i++) {
		var el = $('[name="' + obrigatorios[i].value + '"]').first();
		if (!el.length || !campoDeveAparecerNoResumoDocumento(el)) continue;
		var nome = limparNomeCampoDocumento(obterNomeCampoDocumento(el));
		if (nome) return nome;
	}

	return 'Campo do documento';
}

function exibirModalCamposObrigatoriosDocumento'''
s, n = pat.subn(new, s, count=1)
if n != 1:
    raise SystemExit('Não encontrou obterCampoObrigatorioPrioritarioDocumento')

# 2) No modal, tira somente a caixa vermelha e mantém o texto/label do campo em vermelho.
old = '''\t/* Padrão PBdoc: obrigatório é informado somente no modal, sem pintar campos de vermelho. */
\t$('#frm').find('.is-invalid').each(function() {
\t\tvar campo = $(this);
\t\tremoverElementoInvalido(campo);
\t\tremoverLabelInvalido(campo);
\t\tobterMensagemDivErro(campo).text('');
\t});'''
new2 = '''\t/* Obrigatório: sem borda/caixa vermelha; mantém somente o nome do campo em vermelho. */
\t$('#frm').find('.is-invalid').each(function() {
\t\tvar campo = $(this);
\t\tremoverElementoInvalido(campo);
\t\tobterMensagemDivErro(campo).text('');
\t});'''
if old not in s:
    raise SystemExit('Não encontrou bloco visual do modal')
s = s.replace(old, new2, 1)

# 3) Ao corrigir o valor, limpa também o vermelho do label mesmo se a borda já foi removida pelo modal.
pat2 = re.compile(r"function removerErro\(elemento\) \{.*?\n\}", re.S)
new3 = '''function removerErro(elemento) {
\tremoverElementoInvalido(elemento);
\tremoverLabelInvalido(elemento);
\tobterMensagemDivErro(elemento).text('');
}'''
s, n = pat2.subn(new3, s, count=1)
if n != 1:
    raise SystemExit('Não encontrou removerErro')

js.write_text(s, encoding='utf-8')

# 4) Cache-bust do JS no edita.jsp.
jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
t = jsp.read_text(encoding='utf-8')
t, n = re.subn(r'documento\.validacao\.js\?v=[^"\']+', 'documento.validacao.js?v=pbdoc-validacao-20260817-3', t, count=1)
if n != 1:
    raise SystemExit('Não encontrou versão de documento.validacao.js no edita.jsp')
jsp.write_text(t, encoding='utf-8')
