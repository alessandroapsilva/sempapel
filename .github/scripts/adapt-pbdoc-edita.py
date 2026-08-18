from pathlib import Path
import re

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
js = Path('sigaex/src/main/webapp/javascript/exDocumentoEdita.js')

s = jsp.read_text(encoding='utf-8')

# 1) Garante que o navegador carregue a versão nova do JS de edição.
s = re.sub(
    r'src="\.\./\.\./\.\./javascript/exDocumentoEdita\.js(?:\?v=[^"]*)?"',
    'src="../../../javascript/exDocumentoEdita.js?v=pbdoc-adapt-20260818-2"',
    s,
    count=1,
)

# 2) Mantém a estrutura da release/11.5, mas usa o texto visual do PBdoc nos obrigatórios.
s = s.replace('<span class="text-danger">*</span>', '<a style="color: red">(obrigatório)</a>')

# 3) Não pinta a caixa/input de vermelho. A classe is-invalid continua existindo internamente
#    para a validação funcionar, porém visualmente apenas o label fica vermelho.
css_marker = 'pbdoc-required-visual-20260818'
if css_marker not in s:
    pagina = '<siga:pagina titulo="Novo Documento">'
    css = '''<siga:pagina titulo="Novo Documento">\n\t<style id="pbdoc-required-visual-20260818">\n\t\t#frm .form-control.is-invalid,\n\t\t#frm .custom-select.is-invalid,\n\t\t#frm .custom-file-input.is-invalid ~ .custom-file-label {\n\t\t\tborder-color: #ced4da !important;\n\t\t\tbackground-image: none !important;\n\t\t\tbox-shadow: none !important;\n\t\t}\n\t\t#frm .form-control.is-invalid:focus,\n\t\t#frm .custom-select.is-invalid:focus {\n\t\t\tborder-color: #80bdff !important;\n\t\t\tbox-shadow: 0 0 0 .2rem rgba(0,123,255,.25) !important;\n\t\t}\n\t</style>'''
    if pagina not in s:
        raise SystemExit('Não encontrou abertura siga:pagina no edita.jsp')
    s = s.replace(pagina, css, 1)

# 4) Bump do documento.validacao.js para evitar cache antigo.
s = re.sub(
    r'documento\.validacao\.js(?:\?v=[^"\']*)?',
    'documento.validacao.js?v=pbdoc-adapt-20260818-2',
    s,
    count=1,
)

jsp.write_text(s, encoding='utf-8')

j = js.read_text(encoding='utf-8')

# 5) Validação principal no estilo PBdoc: explícita, sem "Campo obrigatório" genérico.
#    Assunto permanece PRIMEIRO por regra do projeto ENFAS.
start = j.find('function validar(silencioso, finalizar) {')
end = j.find('\nfunction aviso(', start)
if start == -1 or end == -1:
    raise SystemExit('Não encontrou função validar/aviso em exDocumentoEdita.js')

nova_validar = r'''function validar(silencioso, finalizar) {
	personalizacaoJuntar();

	function valor(nome) {
		var el = document.getElementsByName(nome);
		if (!el || !el.length) return '';
		return String(el[0].value || '').trim();
	}

	function valorSelecao(sigla) {
		var id = sigla.replace('Sel.sigla', 'Sel.id');
		var elId = document.getElementsByName(id);
		if (elId && elId.length && String(elId[0].value || '').trim())
			return String(elId[0].value || '').trim();
		return valor(sigla);
	}

	function avisarCampo(nome, elemento) {
		var acao = finalizar ? 'finalizar e assinar o documento' : 'gravar o documento';
		aviso("Preencha o campo '" + nome + "' antes de " + acao + ".", silencioso, elemento);
		return false;
	}

	/* Regra ENFAS: Assunto é sempre o primeiro obrigatório cobrado. */
	var descricaoAutomatica = document.getElementById('descricaoAutomatica');
	var assunto = document.getElementsByName('exDocumentoDTO.descrDocumento');
	if (descricaoAutomatica == null && (!assunto || !assunto.length || !String(assunto[0].value || '').trim())) {
		return avisarCampo('Assunto', assunto && assunto.length ? assunto[0] : null);
	}

	/* Destinatário: usa o nome real da opção escolhida, como no PBdoc. */
	var tipoDestinatarioEl = document.getElementsByName('exDocumentoDTO.tipoDestinatario');
	var tipoDestinatario = tipoDestinatarioEl && tipoDestinatarioEl.length ? String(tipoDestinatarioEl[0].value || '') : '';
	if (tipoDestinatario === '1' && !valorSelecao('exDocumentoDTO.destinatarioSel.sigla')) {
		var destUsuario = document.getElementsByName('exDocumentoDTO.destinatarioSel.sigla');
		return avisarCampo('Destinatário - Usuário', destUsuario && destUsuario.length ? destUsuario[0] : null);
	}
	if (tipoDestinatario === '2' && !valorSelecao('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) {
		var destLotacao = document.getElementsByName('exDocumentoDTO.lotacaoDestinatarioSel.sigla');
		return avisarCampo('Destinatário - Lotação', destLotacao && destLotacao.length ? destLotacao[0] : null);
	}
	if (tipoDestinatario === '3' && !valorSelecao('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) {
		var destOrgao = document.getElementsByName('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla');
		return avisarCampo('Destinatário - Órgão Externo', destOrgao && destOrgao.length ? destOrgao[0] : null);
	}
	if (tipoDestinatario && ['1', '2', '3'].indexOf(tipoDestinatario) === -1 && !valor('exDocumentoDTO.nmDestinatario')) {
		var destLivre = document.getElementsByName('exDocumentoDTO.nmDestinatario');
		return avisarCampo('Destinatário - Campo Livre', destLivre && destLivre.length ? destLivre[0] : null);
	}

	/* Usa o nome adotado na tela desta release, sem copiar JSP de outra versão. */
	if (!valorSelecao('exDocumentoDTO.classificacaoSel.sigla')) {
		var classificacao = document.getElementsByName('exDocumentoDTO.classificacaoSel.sigla');
		return avisarCampo('Classificação Documental', classificacao && classificacao.length ? classificacao[0] : null);
	}

	/* Responsável e substituto, de forma explícita como no PBdoc. */
	var substituicao = document.getElementsByName('exDocumentoDTO.substituicao');
	var substitutoAtivado = substituicao && substituicao.length && substituicao[0].checked;
	if (substitutoAtivado) {
		if (!valorSelecao('exDocumentoDTO.titularSel.sigla')) {
			var titular = document.getElementsByName('exDocumentoDTO.titularSel.sigla');
			return avisarCampo('Substituto Responsável pela Assinatura', titular && titular.length ? titular[0] : null);
		}
	} else if (!valorSelecao('exDocumentoDTO.subscritorSel.sigla')) {
		var subscritorSel = document.getElementsByName('exDocumentoDTO.subscritorSel.sigla');
		return avisarCampo('Responsável pela Assinatura', subscritorSel && subscritorSel.length ? subscritorSel[0] : null);
	}

	/* Campos da entrevista/modelo continuam usando o mecanismo nativo desta versão. */
	if (typeof validarCamposEntrevista === 'function') validarCamposEntrevista();
	var camposInvalidos = $('#frm').find('.is-invalid').not('input[type="hidden"]');
	if (camposInvalidos.length > 0) {
		var primeiro = camposInvalidos.first();
		var nomeCampo = '';
		if (typeof obterNomeCampoDocumento === 'function') nomeCampo = obterNomeCampoDocumento(primeiro);
		if (typeof limparNomeCampoDocumento === 'function') nomeCampo = limparNomeCampoDocumento(nomeCampo);

		if (!nomeCampo || /^(Campo obrigatório|um campo obrigatório)$/i.test(nomeCampo)) {
			var name = String(primeiro.attr('name') || '').trim();
			nomeCampo = name
				.replace(/^exDocumentoDTO\./, '')
				.replace(/Sel\.sigla$/, '')
				.replace(/_/g, ' ')
				.replace(/([A-Z])/g, ' $1')
				.replace(/\s+/g, ' ')
				.trim();
		}

		if (!nomeCampo || /^(Campo obrigatório|um campo obrigatório)$/i.test(nomeCampo))
			nomeCampo = 'Campo do modelo';

		return avisarCampo(nomeCampo, primeiro[0]);
	}

	var eletroHidden = document.getElementById('eletronicoHidden');
	var eletro1 = document.getElementById('eletronicoCheck1');
	var eletro2 = document.getElementById('eletronicoCheck2');
	var hasPai = document.getElementById('hasPai');
	var isPaiEletronico = document.getElementById('isPaiEletronico');
	var subscritor = document.getElementById('formulario_exDocumentoDTO.subscritorSel_id');
	var temCossignatarios = document.getElementById('temCossignatarios');

	if ((temCossignatarios && temCossignatarios.value === 'true') && (!subscritor || !subscritor.value)) {
		aviso('É necessário informar um subscritor, pois o documento possui cossignatários', silencioso);
		return false;
	}
	if (eletroHidden == null && eletro1 && eletro2 && !eletro1.checked && !eletro2.checked) {
		aviso('É necessário informar se o documento será digital ou físico, na parte superior da tela.', silencioso);
		return false;
	}
	if (eletroHidden == null && hasPai && isPaiEletronico && hasPai.value === 'true' && eletro1 && eletro2) {
		if (isPaiEletronico.value == 'true' && eletro2.checked) {
			aviso('O documento deve ser digital, não pode ser de outro tipo.', silencioso);
			return false;
		}
		if (isPaiEletronico.value == 'false' && eletro1.checked) {
			aviso('O documento deve ser físico, não pode ser de outro tipo.', silencioso);
			return false;
		}
	}

	var limiteEl = document.getElementsByName('exDocumentoDTO.tamanhoMaximoDescricao');
	if (limiteEl && limiteEl.length && assunto && assunto.length) {
		var limite = limiteEl[0].value;
		if (assunto[0].value.length >= limite) {
			aviso('O tamanho máximo da descrição é de ' + limite + ' caracteres', silencioso);
			return false;
		}
	}

	var personalizacao = document.getElementById('frm_nmFuncaoSubscritor');
	if (personalizacao && personalizacao.value.length > 128) {
		aviso('O tamanho máximo da soma dos caracteres de personalização é de 128 caracteres', silencioso);
		return false;
	}

	return true;
}
'''

j = j[:start] + nova_validar + j[end:]
js.write_text(j, encoding='utf-8')
