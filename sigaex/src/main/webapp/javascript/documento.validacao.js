var funcoesCallback = [];

function adicionarFuncaoParaValidacao(elemento, funcao) {
	if (!(elemento instanceof jQuery)) {
		elemento = $(elemento);
	}
	
	funcoesCallback.push({ elemento, funcao });
}

function executarFuncoesCallback() {
	funcoesCallback.forEach(function(item) {		
		if (item.elemento.length > 0 && typeof item.funcao === 'function') {
			var obrigatorio = $('input[type=hidden][name=obrigatorios][value="' + item.elemento.attr('name') + '"]');
			
			if (obrigatorio.length == 0 || (obrigatorio.length > 0 && !item.elemento.hasClass('is-invalid'))) {
				executarFuncao(item.elemento, item.funcao);
			}															
		}					
	});
}

function executarFuncao(elemento, funcao) {
	try {
		var resultado = funcao.call();
		
		if (typeof resultado === 'string' && resultado.trim() != '') {
			aplicarErro(elemento, resultado);				
		} else {
			removerErro(elemento);
		}
	} catch (err) {
		console.log('Não foi possível executar a função: \n' + funcao + '\n Erro: ' + err.message);
	}
}

function criarIds() {
	$('#frm').find('[data-criar-id="true"]').each(function(index, value) {				
		if (value.id === '') {
			var input = $(value);
			var label = input.parent().find('[data-nome-ref="' + value.name + '"]');
			var id = value.name.concat(index);
			
			input.attr('id', id);
			label.attr('for', id);			
		}		
	});
}

function validarCamposEntrevista() {
	var obrigatorios = $('#frm').find('[name=obrigatorios]');		
	
	obrigatorios.each(function() {
		var elemento = $('[name="' + this.value + '"]');
		if (elemento.length == 0 || !campoDeveSerValidadoDocumento(elemento)) {
			return;
		}

		var fieldName = this.value.replace("Sel.sigla", "Sel.id");
		var valor = $('[name="' + fieldName + '"]').val();
		
		var temCpf = !!elemento.data('formatarCpf');
		var temCnpj = !!elemento.data('formatarCnpj');
		
		if (valor == null || valor === '' || !valor || /^\s*$/.test(valor)) {
			var tituloLabel = obterLabel(elemento);				
			var mensagem = 'Favor preencher o campo';
			
			if (tituloLabel.text().length > 0) {								
				if (temCpf || temCnpj) {
					mensagem = mensagem.concat(' '.concat(tituloLabel.text().trim()));					
				} else {
					mensagem = mensagem.concat(' '.concat(tituloLabel.text().trim().toLowerCase()));					
				}
				mensagem = mensagem.replace(':', ' ');
			}
			
			aplicarErro(elemento, mensagem);						
		} else {
			removerErro(elemento);																						
		}
							
		if (valor && (valor.length > 0 || !/^\s*$/.test(valor))) {			
			if (elemento.hasClass('campoData')) {
				validarData(elemento);				
			}
						
			if (elemento.hasClass('campoHoraMinuto')) {
				validarHoraMinuto(elemento);				
			}
											
			if (temCpf) {
				validarCpf(elemento);																			
			} 
											
			if (temCnpj) {
				validarCnpj(elemento);
			}							
		}
						
		validarSelect(elemento);							
		validarInputRadioECheckbox(elemento);
		
	});	
	
	validarDocumentoCapturado();	
	executarFuncoesCallback();
}

function obterMensagensCamposInvalidosDocumento() {
	var mensagens = [];
	var mensagensAdicionadas = {};

	$('#frm').find('.is-invalid').each(function() {
		var elemento = $(this);
		if (!campoDeveAparecerNoResumoDocumento(elemento)) {
			return;
		}

		var mensagem = obterMensagemCampoInvalidoDocumento(elemento);

		if (mensagem && !mensagensAdicionadas[mensagem]) {
			mensagensAdicionadas[mensagem] = true;
			mensagens.push(mensagem);
		}
	});

	return mensagens;
}

function obterMensagemCampoInvalidoDocumento(elemento) {
	var mensagem = obterMensagemDivErro(elemento).filter(function() {
		return $(this).text().trim().length > 0;
	}).first().text().trim();

	if (mensagem) {
		return mensagem;
	}

	var label = obterNomeCampoDocumento(elemento);

	if (label.length > 0) {
		return 'Favor preencher o campo ' + label;
	}

	return 'Favor preencher um campo obrigatório';
}

function obterPrimeiroCampoInvalidoDocumento() {
	var campo = $('#frm').find('.is-invalid').filter(function() {
		return campoDeveAparecerNoResumoDocumento($(this));
	}).first();

	if (campo.length == 0) {
		campo = $('#frm').find('.is-invalid').first();
	}

	return campo.length > 0 ? campo[0] : null;
}

function exibirModalCamposObrigatoriosDocumento(mensagens, finalizar) {
	var elemento = obterPrimeiroCampoInvalidoDocumento();
	var cabecalho = finalizar
			? 'Os seguintes campos obrigatórios precisam ser preenchidos antes de finalizar e assinar:'
			: 'Os seguintes campos obrigatórios precisam ser preenchidos antes de gravar:';
	var msg = cabecalho + '\n\n- ' + mensagens.join('\n- ');

	if (typeof sigaModal !== 'undefined' && typeof sigaModal.alerta === 'function') {
		var modal = sigaModal.alerta(msg);
		if (modal && typeof modal.focus === 'function') {
			modal.focus(elemento);
		}
	} else {
		alert(msg);
		if (elemento && typeof elemento.focus === 'function') {
			elemento.focus();
		}
	}
}

function validarCamposObrigatoriosEditaDocumento() {
	validarCampoObrigatorioDocumento('exDocumentoDTO.dtDocString', 'Favor preencher o campo data');
	validarSelecaoObrigatoriaDocumento('exDocumentoDTO.subscritorSel.sigla', 'Favor preencher o campo responsável pela assinatura');

	if ($('#substitutoSwitch').is(':checked')) {
		validarSelecaoObrigatoriaDocumento('exDocumentoDTO.titularSel.sigla', 'Favor preencher o campo substituto do responsável pela assinatura');
	} else {
		removerErroCampoDocumento('exDocumentoDTO.titularSel.sigla');
	}

	validarDestinatarioObrigatorioDocumento();
	validarSelecaoObrigatoriaDocumento('exDocumentoDTO.classificacaoSel.sigla', 'Favor preencher o campo classificação documental');
	validarCampoObrigatorioDocumento('exDocumentoDTO.descrDocumento', 'Favor preencher o campo assunto');
	validarCamposRequiredDocumento();
}

function validarDestinatarioObrigatorioDocumento() {
	var tipoDestinatario = $('[name="exDocumentoDTO.tipoDestinatario"]').val();

	if (!tipoDestinatario) {
		return;
	}

	if (tipoDestinatario == '1') {
		validarSelecaoObrigatoriaDocumento('exDocumentoDTO.destinatarioSel.sigla', 'Favor preencher o campo destinatário');
	} else if (tipoDestinatario == '2') {
		validarSelecaoObrigatoriaDocumento('exDocumentoDTO.lotacaoDestinatarioSel.sigla', 'Favor preencher o campo destinatário');
	} else if (tipoDestinatario == '3') {
		validarSelecaoObrigatoriaDocumento('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla', 'Favor preencher o campo destinatário');
	} else {
		validarCampoObrigatorioDocumento('exDocumentoDTO.nmDestinatario', 'Favor preencher o campo destinatário');
	}
}

function validarSelecaoObrigatoriaDocumento(nomeCampoSigla, mensagem) {
	var elemento = $('[name="' + nomeCampoSigla + '"]').first();

	if (elemento.length == 0 || !campoDeveSerValidadoDocumento(elemento)) {
		return;
	}

	var nomeCampoId = nomeCampoSigla.replace('Sel.sigla', 'Sel.id');
	var campoId = $('[name="' + nomeCampoId + '"]').first();
	var valor = campoId.length > 0 ? campoId.val() : elemento.val();

	validarValorObrigatorioDocumento(elemento, valor, mensagem);
}

function validarCampoObrigatorioDocumento(nomeCampo, mensagem) {
	var elemento = $('[name="' + nomeCampo + '"]').first();

	if (elemento.length == 0 || !campoDeveSerValidadoDocumento(elemento)) {
		return;
	}

	validarValorObrigatorioDocumento(elemento, elemento.val(), mensagem || montarMensagemCampoObrigatorioDocumento(elemento));
}

function validarCamposRequiredDocumento() {
	$('#frm').find('[required], [aria-required="true"]').each(function() {
		var elemento = $(this);

		if (!campoDeveSerValidadoDocumento(elemento)) {
			return;
		}

		validarValorObrigatorioDocumento(elemento, elemento.val(), montarMensagemCampoObrigatorioDocumento(elemento));
	});
}

function campoDeveSerValidadoDocumento(elemento) {
	return elemento
			&& elemento.length > 0
			&& !elemento.is(':disabled')
			&& elemento.attr('type') !== 'hidden'
			&& elemento.closest('[style*="display: none"], .d-none, [hidden]').length == 0;
}

function campoDeveAparecerNoResumoDocumento(elemento) {
	return elemento
			&& elemento.length > 0
			&& elemento.attr('type') !== 'hidden'
			&& elemento.closest('[style*="display: none"], .d-none, [hidden]').length == 0;
}

function removerErroCampoDocumento(nomeCampo) {
	var elemento = $('[name="' + nomeCampo + '"]').first();

	if (elemento.length > 0) {
		removerErro(elemento);
	}
}

function validarValorObrigatorioDocumento(elemento, valor, mensagem) {
	if (valor == null || valor === '' || !valor || /^\s*$/.test(valor)) {
		aplicarErro(elemento, mensagem || montarMensagemCampoObrigatorioDocumento(elemento));
	} else {
		removerErro(elemento);
	}
}

function montarMensagemCampoObrigatorioDocumento(elemento) {
	var nomeCampo = obterNomeCampoDocumento(elemento);

	if (nomeCampo.length > 0) {
		return 'Favor preencher o campo ' + nomeCampo;
	}

	return 'Favor preencher um campo obrigatório';
}

function validarData(elemento) {
	var resultado = verifica_data(elemento[0], false, true);
	
	if (typeof resultado === 'string' && resultado.length > 0) {
		aplicarErro(elemento, resultado.concat('. Favor preencher neste formato ex.: ' + $.datepicker.formatDate('dd/mm/yy', new Date())));
	}
	
	if (typeof resultado === 'boolean' && !resultado) {
		aplicarErro(elemento, 'Data inválida');
	}
}

function validarHoraMinuto(elemento) {
	var resultado = verifica_hora(elemento[0], false, true);
	
	if (typeof resultado === 'string' && resultado.length > 0) {
		var horaMinutoAtual = new Date();
		
		aplicarErro(elemento, resultado.concat('. Favor preencher neste formato ex.: ' + horaMinutoAtual.getHours() + ':' + horaMinutoAtual.getMinutes()));
	}
	
	if (typeof resultado === 'boolean' && !resultado) {
		aplicarErro(elemento, 'Data inválida');
	}
}

function validarCpf(elemento) {
	if (!isCpfValido(elemento.val())) {
		aplicarErro(elemento, 'Favor informar um CPF válido');
	}		
}

function validarCnpj(elemento) {
	if (!isCnpjValido(elemento.val())) {
		aplicarErro(elemento, 'Favor informar um CNPJ válido');
	}				
}

function validarSelect(elemento) {
	if (elemento[0] && elemento[0].tagName === 'SELECT') {
		var option = elemento.find(':selected');
		if (option.length > 0 && (option.attr('id') === 'opcaoNeutra' || option.val() === '')) {
			aplicarErro(elemento, 'Favor selecione uma opção');
		}
	}
}

function validarInputRadioECheckbox(elemento) {
	if(elemento[0] && elemento[0].tagName === 'INPUT' && (elemento[0].type === 'radio' || elemento[0].type === 'checkbox')) {
		var checado = $('input[name="' + elemento.attr('name') + '"]:checked');
		if (checado.length == 0) {				
			aplicarErro(elemento, 'Favor selecionar alguma opção');									
		}
	}
}

function validarDocumentoCapturado() {
	var origem = document.getElementsByName('exDocumentoDTO.idTpDoc')[0].value;
	var id = document.getElementsByName('exDocumentoDTO.id')[0].value;
	if ((origem == 4 || origem == 5) && !id) {
		// Capturado PDF
		var arquivo = document.getElementsByName('arquivo')[0]; 

		if (!arquivo.classList.contains('is-invalid')) {
			if (arquivo.value == "") {
				var mensagem = 'Documento capturado não pode ser gravado sem que seja informado o arquivo PDF.';
				aplicarErro($(arquivo), mensagem);					
			} else {
				removerErro($(arquivo));
			}						
		}
	} else {		
		if (origem == 6 || origem == 7) {
			// Capturado de formato livre
			let linkArq = document.getElementById('linkArquivo');
			let arqUpload = document.getElementById('arqUpload');
			
			if (linkArq && linkArq.innerText === "" && !linkArq.classList.contains('is-invalid')) {
				var mensagem = 'Documento capturado não pode ser gravado sem que seja informado o arquivo.';
				aplicarErro($(arqUpload), mensagem);
			} else {
				removerErro($(arqUpload));				
			}					
		}		
	}
}

function aplicarErro(elemento, mensagem) {		
	aplicarElementoInvalido(elemento);
	aplicarLabelInvalido(elemento);	
	aplicarMensagemErro(elemento, mensagem);									
}

function removerErro(elemento) {			
	if (elemento.hasClass('is-invalid')) {		
		removerElementoInvalido(elemento);						
		removerLabelInvalido(elemento);
	}
}

function aplicarElementoInvalido(elemento) {
	elemento.addClass('is-invalid');
}

function aplicarLabelInvalido(elemento) {
	var tituloLabel = obterLabel(elemento);
	var nome = elemento.attr('name');
	
	if (tituloLabel.length > 0) {
		if (!tituloLabel.hasClass('titulo-'.concat(nome))) {
			tituloLabel.addClass('titulo-'.concat(nome));
		}					
		tituloLabel.css('color', '#dc3545');
	}
}

function removerElementoInvalido(elemento) {
	elemento.removeClass('is-invalid');
}

function removerLabelInvalido(elemento) {
	var nome = elemento.attr('name');	
	var tituloLabel = $('.titulo-'.concat(nome));
	
	if (tituloLabel.length == 0) {
		tituloLabel = obterLabel(elemento);
	}
	
	if (tituloLabel.length > 0) {
		tituloLabel.removeClass('titulo-'.concat(nome));
		tituloLabel.css('color', 'black');
	}	
}

function aplicarMensagemErro(elemento, mensagem) {
	var mensagemDiv = obterMensagemDivErro(elemento);
	if (mensagemDiv.length == 0) {
		var nomeCampo = elemento.attr('name');
		mensagemDiv = $('<div/>', {
			'class': 'invalid-feedback invalid-feedback-' + normalizarNomeCampoDocumento(nomeCampo)
		});
		mensagemDiv.attr('data-campo-documento', nomeCampo);

		elemento.closest('.form-group, .custom-file').append(mensagemDiv);
	}
	
	if (mensagemDiv.length > 0) {
		if (elemento[0].type === 'radio' || elemento[0].type === 'checkbox') {
			mensagemDiv.text('');
			mensagemDiv.last().text(mensagem);
		} else {
			mensagemDiv.text(mensagem);
		}				
	}
}

function obterMensagemDivErro(elemento) {
	var nomeCampo = elemento.attr('name');
	var mensagemDiv = $('.invalid-feedback[data-campo-documento="' + nomeCampo + '"]');

	if (mensagemDiv.length == 0) {
		mensagemDiv = $('.invalid-feedback-' + normalizarNomeCampoDocumento(nomeCampo));
	}

	if (mensagemDiv.length == 0 && /^[A-Za-z0-9_-]+$/.test(nomeCampo)) {
		mensagemDiv = $('.invalid-feedback-' + nomeCampo);
	}

	return mensagemDiv;
}

function normalizarNomeCampoDocumento(nomeCampo) {
	return String(nomeCampo || '').replace(/[^A-Za-z0-9_-]/g, '_');
}

function obterNomeCampoDocumento(elemento) {
	var label = '';
	var tituloLabel = obterLabel(elemento);

	if (tituloLabel && tituloLabel.length > 0) {
		label = tituloLabel.clone().children().remove().end().text();
	}

	if (!label) {
		label = elemento.attr('aria-label')
				|| elemento.attr('title')
				|| elemento.attr('placeholder')
				|| elemento.data('nome')
				|| elemento.data('label')
				|| '';
	}

	if (!label) {
		var nomeCampo = elemento.attr('name') || '';
		label = nomeCampo.replace(/^exDocumentoDTO\./, '')
				.replace(/Sel\.sigla$/, '')
				.replace(/([A-Z])/g, ' $1')
				.replace(/\./g, ' ');
	}

	return limparNomeCampoDocumento(label);
}

function limparNomeCampoDocumento(label) {
	return String(label || '')
			.replace(/\*/g, '')
			.replace(/\(obrigatório\)/ig, '')
			.replace(/:/g, '')
			.replace(/\s+/g, ' ')
			.trim()
			.toLowerCase();
}

function obterLabel(elemento) {
	var elementoName = elemento.attr('name');
	if (!elementoName) return $();
	var fieldName = elementoName.replace(/_[A-Za-z0-9_]+Sel\.sigla$/, "");
	var elementoId = elemento.attr('id');
	var tituloLabel = elementoId ? $('label[for="' + elementoId + '"]') : $();
	
	if (tituloLabel.length == 0) {
		tituloLabel = $('label[for="' + fieldName + '"]');
	}

	if (tituloLabel.length == 0) {
		tituloLabel = $('[data-nome-ref="' + elementoName + '"]');
	}

	if (tituloLabel.length == 0) {
		tituloLabel = elemento.closest('.form-group, .row, .form-row').find('label, .control-label, .col-form-label, span, b').filter(function() {
			return limparNomeCampoDocumento($(this).text()).length > 0;
		}).first();
	}

	if (tituloLabel.length == 0) {
		var tag = elemento.parent().prev();		
		
		if (tag.length > 0 && (tag[0].tagName === 'LABEL' || tag[0].tagName === 'SPAN' || tag[0].tagName === 'B')) {
			tituloLabel = tag;
		} else {
			tag = elemento.prev();
			
			if (tag.length > 0 && (tag[0].tagName === 'LABEL' || tag[0].tagName === 'SPAN' || tag[0].tagName === 'B')) {
				tituloLabel = tag;
			}				
		}	
		
		if (tag.length > 0 && tag.data('toggle') === 'tooltip') {
			tag = tag.prev();
			
			if (tag.length > 0 && (tag[0].tagName === 'LABEL' || tag[0].tagName === 'SPAN' || tag[0].tagName === 'B')) {
				tituloLabel = tag;
			}				
		}
	}	
	
	return tituloLabel;
}

function isCpfValido(cpf) {	
	cpf = cpf.replace(/[^\d]+/g,'');	
    if(cpf == '') return false;	
    // Elimina CPFs invalidos conhecidos	
    if (cpf.length != 11 || 
        cpf == "00000000000" || 
        cpf == "11111111111" || 
        cpf == "22222222222" || 
        cpf == "33333333333" || 
        cpf == "44444444444" || 
        cpf == "55555555555" || 
        cpf == "66666666666" || 
        cpf == "77777777777" || 
        cpf == "88888888888" || 
        cpf == "99999999999")
      return false;		
    // Valida 1o digito	
    add = 0;	
    for (i=0; i < 9; i ++)		
      add += parseInt(cpf.charAt(i)) * (10 - i);	
    rev = 11 - (add % 11);	
    if (rev == 10 || rev == 11)		
      rev = 0;	
    if (rev != parseInt(cpf.charAt(9)))		
      return false;		
    // Valida 2o digito	
    add = 0;	
    for (i = 0; i < 10; i ++)		
      add += parseInt(cpf.charAt(i)) * (11 - i);	
    rev = 11 - (add % 11);	
    if (rev == 10 || rev == 11)	
      rev = 0;	
    if (rev != parseInt(cpf.charAt(10)))
      return false;		
    return true;   
}

function isCnpjValido(cnpj) {
    cnpj = cnpj.replace(/[^\d]+/g,'');

    if(cnpj == '') return false;

    if (cnpj.length != 14)
      return false;

    // Elimina CNPJs invalidos conhecidos
    if (cnpj == "00000000000000" || 
        cnpj == "11111111111111" || 
        cnpj == "22222222222222" || 
        cnpj == "33333333333333" || 
        cnpj == "44444444444444" || 
        cnpj == "55555555555555" || 
        cnpj == "66666666666666" || 
        cnpj == "77777777777777" || 
        cnpj == "88888888888888" || 
        cnpj == "99999999999999")
      return false;

    // Valida DVs
    tamanho = cnpj.length - 2
      numeros = cnpj.substring(0,tamanho);
    digitos = cnpj.substring(tamanho);
    soma = 0;
    pos = tamanho - 7;
    for (i = tamanho; i >= 1; i--) {
      soma += numeros.charAt(tamanho - i) * pos--;
      if (pos < 2)
        pos = 9;
    }
    resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado != digitos.charAt(0))
      return false;

    tamanho = tamanho + 1;
    numeros = cnpj.substring(0,tamanho);
    soma = 0;
    pos = tamanho - 7;
    for (i = tamanho; i >= 1; i--) {
      soma += numeros.charAt(tamanho - i) * pos--;
      if (pos < 2)
        pos = 9;
    }
    resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado != digitos.charAt(1))
      return false;

    return true;
}
  
$(function() {
	criarIds();			
});
