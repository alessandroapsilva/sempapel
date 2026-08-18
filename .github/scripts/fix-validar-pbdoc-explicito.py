from pathlib import Path
import re

p = Path('sigaex/src/main/webapp/javascript/exDocumentoEdita.js')
s = p.read_text(encoding='utf-8')

pat = re.compile(r"function validar\(silencioso, finalizar\) \{.*?\n\}\n\nfunction aviso\(", re.S)

new = r'''function validar(silencioso, finalizar) {
	personalizacaoJuntar();

	function valor(nome) {
		var el = document.getElementsByName(nome);
		if (!el || !el.length) return '';
		return String(el[0].value || '').trim();
	}

	function valorSelecao(sigla) {
		var id = sigla.replace('Sel.sigla', 'Sel.id');
		var elId = document.getElementsByName(id);
		if (elId && elId.length && String(elId[0].value || '').trim()) return String(elId[0].value || '').trim();
		return valor(sigla);
	}

	function avisarCampo(nome, elemento) {
		var acao = finalizar ? 'finalizar e assinar o documento' : 'gravar o documento';
		aviso("Preencha o campo '" + nome + "' antes de " + acao + ".", silencioso, elemento);
		return false;
	}

	/* Igual ao PBdoc, porém com Assunto como PRIMEIRO obrigatório, conforme regra ENFAS. */
	var descricaoAutomatica = document.getElementById('descricaoAutomatica');
	var assunto = document.getElementsByName('exDocumentoDTO.descrDocumento');
	if (descricaoAutomatica == null && (!assunto || !assunto.length || !String(assunto[0].value || '').trim())) {
		return avisarCampo('Assunto', assunto && assunto.length ? assunto[0] : null);
	}

	/* Destinatário: nome exato conforme a opção exibida na tela. */
	var tipoDestinatarioEl = document.getElementsByName('exDocumentoDTO.tipoDestinatario');
	var tipoDestinatario = tipoDestinatarioEl && tipoDestinatarioEl.length ? String(tipoDestinatarioEl[0].value || '') : '';
	if (tipoDestinatario === '1' && !valorSelecao('exDocumentoDTO.destinatarioSel.sigla')) {
		var e1 = document.getElementsByName('exDocumentoDTO.destinatarioSel.sigla');
		return avisarCampo('Destinatário - Usuário', e1 && e1.length ? e1[0] : null);
	}
	if (tipoDestinatario === '2' && !valorSelecao('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) {
		var e2 = document.getElementsByName('exDocumentoDTO.lotacaoDestinatarioSel.sigla');
		return avisarCampo('Destinatário - Lotação', e2 && e2.length ? e2[0] : null);
	}
	if (tipoDestinatario === '3' && !valorSelecao('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) {
		var e3 = document.getElementsByName('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla');
		return avisarCampo('Destinatário - Órgão Externo', e3 && e3.length ? e3[0] : null);
	}
	if (tipoDestinatario && ['1','2','3'].indexOf(tipoDestinatario) === -1 && !valor('exDocumentoDTO.nmDestinatario')) {
		var e4 = document.getElementsByName('exDocumentoDTO.nmDestinatario');
		return avisarCampo('Destinatário - Campo Livre', e4 && e4.length ? e4[0] : null);
	}

	/* Classificação: usa exatamente o nome da tela ENFAS. */
	if (!valorSelecao('exDocumentoDTO.classificacaoSel.sigla')) {
		var cl = document.getElementsByName('exDocumentoDTO.classificacaoSel.sigla');
		return avisarCampo('Classificação Documental', cl && cl.length ? cl[0] : null);
	}

	/* Responsável / substituto, no estilo explícito do PBdoc. */
	var substituicao = document.getElementsByName('exDocumentoDTO.substituicao');
	var substitutoAtivado = substituicao && substituicao.length && substituicao[0].checked;
	if (substitutoAtivado) {
		if (!valorSelecao('exDocumentoDTO.titularSel.sigla')) {
			var tit = document.getElementsByName('exDocumentoDTO.titularSel.sigla');
			return avisarCampo('Substituto Responsável pela Assinatura', tit && tit.length ? tit[0] : null);
		}
	} else if (!valorSelecao('exDocumentoDTO.subscritorSel.sigla')) {
		var sub = document.getElementsByName('exDocumentoDTO.subscritorSel.sigla');
		return avisarCampo('Responsável pela Assinatura', sub && sub.length ? sub[0] : null);
	}

	/* Campos obrigatórios da entrevista/modelo: mantém a validação genérica só para eles. */
	validarCamposEntrevista();
	var camposInvalidos = $('#frm').find('.is-invalid').not('input[type="hidden"]');
	if (camposInvalidos.length > 0) {
		var primeiro = camposInvalidos.first();
		var nomeCampo = '';
		if (typeof obterNomeCampoDocumento === 'function') nomeCampo = obterNomeCampoDocumento(primeiro);
		if (typeof limparNomeCampoDocumento === 'function') nomeCampo = limparNomeCampoDocumento(nomeCampo);
		if (!nomeCampo || /^(Campo obrigatório|um campo obrigatório)$/i.test(nomeCampo)) {
			/* Nunca exibir o texto genérico. Usa name como último fallback legível. */
			nomeCampo = String(primeiro.attr('name') || 'Campo do modelo')
				.replace(/^exDocumentoDTO\./, '')
				.replace(/Sel\.sigla$/, '')
				.replace(/_/g, ' ')
				.replace(/([A-Z])/g, ' $1')
				.trim();
		}
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

	var limite = document.getElementsByName('exDocumentoDTO.tamanhoMaximoDescricao')[0].value;
	if (assunto && assunto.length && assunto[0].value.length >= limite) {
		aviso('O tamanho máximo da descrição é de ' + limite + ' caracteres', silencioso);
		return false;
	}
	if (document.getElementById('frm_nmFuncaoSubscritor').value.length > 128) {
		aviso('O tamanho máximo da soma dos caracteres de personalização é de 128 caracteres', silencioso);
		return false;
	}

	return true;
}

function aviso('''

s2, n = pat.subn(new, s, count=1)
if n != 1:
    raise SystemExit('Não encontrou function validar(silencioso, finalizar)')
p.write_text(s2, encoding='utf-8')

# Cache-bust do exDocumentoEdita.js no JSP
jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
t = jsp.read_text(encoding='utf-8')
t, n = re.subn(r'exDocumentoEdita\.js\?v=[^"\']+', 'exDocumentoEdita.js?v=pbdoc-explicito-20260818-1', t, count=1)
if n == 0:
    t, n = re.subn(r'exDocumentoEdita\.js', 'exDocumentoEdita.js?v=pbdoc-explicito-20260818-1', t, count=1)
if n != 1:
    raise SystemExit('Não encontrou exDocumentoEdita.js no edita.jsp')
jsp.write_text(t, encoding='utf-8')
