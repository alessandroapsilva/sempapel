(function(window, document, $) {
    'use strict';

    if (!$) return;

    function clean(text) {
        return String(text || '')
            .replace(/\(obrigat[oó]rio\)/ig, '')
            .replace(/\*/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function byName(name) {
        var els = document.getElementsByName(name);
        return els && els.length ? els[0] : null;
    }

    function hasValue(el) {
        return !!(el && String($(el).val() || '').trim());
    }

    function selectionHasValue(siglaName) {
        var sigla = byName(siglaName);
        var id = byName(siglaName.replace('Sel.sigla', 'Sel.id'));
        return hasValue(sigla) || hasValue(id);
    }

    function avisoPbdoc(msg, silencioso, elemento) {
        var btn = document.getElementById('btnGravar');
        if (btn) btn.disabled = false;
        var btnFinalizar = document.getElementById('btnFinalizarAssinar');
        if (btnFinalizar) btnFinalizar.disabled = false;

        if (silencioso) {
            if (typeof window.avisoVermelho === 'function') {
                window.avisoVermelho('O documento não pôde ser salvo: ' + msg);
            }
            return false;
        }

        if (window.sigaModal && typeof window.sigaModal.alerta === 'function') {
            window.sigaModal.alerta(msg).focus(elemento);
        } else {
            window.alert(msg);
        }
        return false;
    }

    function nomeCampoInvalido(el) {
        if (!el) return '';
        var key = el.name || el.id || '';
        var conhecidos = {
            'exDocumentoDTO.descrDocumento': 'Assunto',
            'descrDocumento': 'Assunto',
            'exDocumentoDTO.subscritorSel.sigla': 'Responsável pela Assinatura',
            'exDocumentoDTO.subscritorSel.id': 'Responsável pela Assinatura',
            'exDocumentoDTO.titularSel.sigla': 'Substituto Responsável pela Assinatura',
            'exDocumentoDTO.titularSel.id': 'Substituto Responsável pela Assinatura',
            'exDocumentoDTO.classificacaoSel.sigla': 'Tipo Documental',
            'exDocumentoDTO.classificacaoSel.id': 'Tipo Documental',
            'exDocumentoDTO.destinatarioSel.sigla': 'Destinatário - Usuário',
            'exDocumentoDTO.destinatarioSel.id': 'Destinatário - Usuário',
            'exDocumentoDTO.lotacaoDestinatarioSel.sigla': 'Destinatário - Lotação',
            'exDocumentoDTO.lotacaoDestinatarioSel.id': 'Destinatário - Lotação',
            'exDocumentoDTO.orgaoExternoDestinatarioSel.sigla': 'Destinatário - Órgão Externo',
            'exDocumentoDTO.orgaoExternoDestinatarioSel.id': 'Destinatário - Órgão Externo',
            'exDocumentoDTO.nmDestinatario': 'Destinatário - Campo Livre',
            'personalizarFuncao': 'Função',
            'personalizarUnidade': 'Lotação',
            'personalizarLocalidade': 'Cidade',
            'personalizarNome': 'Nome'
        };
        if (conhecidos[key]) return conhecidos[key];

        if (typeof window.obterLabel === 'function') {
            try {
                var lbl = window.obterLabel($(el));
                if (lbl && lbl.length) {
                    var t = clean(lbl.text());
                    if (t) return t;
                }
            } catch (e) {}
        }

        var group = $(el).closest('.form-group');
        var label = group.find('label').first().clone();
        label.find('a,span,i,small').remove();
        var text = clean(label.text());
        if (text && !/Campo obrigat[oó]rio/i.test(text)) return text;
        return '';
    }

    function limparFavorPreencherInline() {
        $('#frm .is-invalid').each(function() {
            var name = this.name || '';
            if (!name) return;
            $('.invalid-feedback-' + name.replace(/([:.\[\],=@])/g, '\\$1')).each(function() {
                var txt = clean($(this).text());
                if (/^Favor\s+(preencher|informar|selecionar)/i.test(txt)) $(this).text('');
            });
        });
    }

    function validarPbdoc(silencioso) {
        if (typeof window.personalizacaoJuntar === 'function') window.personalizacaoJuntar();

        var descr = byName('exDocumentoDTO.descrDocumento');
        var descricaoAutomatica = document.getElementById('descricaoAutomatica');
        var responsavel = byName('exDocumentoDTO.subscritorSel.sigla');
        var substituicao = byName('exDocumentoDTO.substituicao');
        var titular = byName('exDocumentoDTO.titularSel.sigla');

        /* Regra ENFAS mantida: Assunto é o primeiro obrigatório a ser avisado. */
        if (descricaoAutomatica == null && (!descr || !String(descr.value || '').trim())) {
            return avisoPbdoc("Preencha o campo 'Assunto' antes de gravar o documento.", silencioso, descr);
        }

        if (!responsavel || !String(responsavel.value || '').trim()) {
            return avisoPbdoc("Preencha o campo 'Responsável pela Assinatura' antes de gravar o documento.", silencioso, responsavel);
        }

        if (substituicao && substituicao.checked && (!titular || !String(titular.value || '').trim())) {
            return avisoPbdoc("Preencha o campo 'Substituto Responsável pela Assinatura' antes de gravar o documento.", silencioso, titular);
        }

        var classificacao = document.getElementById('formulario_exDocumentoDTO.classificacaoSel_id') || byName('exDocumentoDTO.classificacaoSel.id');
        if (!classificacao || !String(classificacao.value || '').trim()) {
            return avisoPbdoc("Preencha o campo 'Tipo Documental' antes de gravar o documento.", silencioso, classificacao);
        }

        var tipoDest = byName('exDocumentoDTO.tipoDestinatario');
        if (tipoDest) {
            var tipo = String(tipoDest.value || '');
            if (tipo === '1' && !selectionHasValue('exDocumentoDTO.destinatarioSel.sigla')) {
                return avisoPbdoc("Preencha o campo 'Destinatário - Usuário' antes de gravar o documento.", silencioso, byName('exDocumentoDTO.destinatarioSel.sigla'));
            }
            if (tipo === '2' && !selectionHasValue('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) {
                return avisoPbdoc("Preencha o campo 'Destinatário - Lotação' antes de gravar o documento.", silencioso, byName('exDocumentoDTO.lotacaoDestinatarioSel.sigla'));
            }
            if (tipo === '3' && !selectionHasValue('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) {
                return avisoPbdoc("Preencha o campo 'Destinatário - Órgão Externo' antes de gravar o documento.", silencioso, byName('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla'));
            }
            if (tipo !== '1' && tipo !== '2' && tipo !== '3') {
                var livre = byName('exDocumentoDTO.nmDestinatario');
                if (livre && !String(livre.value || '').trim()) {
                    return avisoPbdoc("Preencha o campo 'Destinatário - Campo Livre' antes de gravar o documento.", silencioso, livre);
                }
            }
        }

        var personalizacao = byName('exDocumentoDTO.personalizacao');
        if (personalizacao && personalizacao.checked) {
            var camposPersonalizacao = [
                ['personalizarFuncao', 'Função'],
                ['personalizarUnidade', 'Lotação'],
                ['personalizarLocalidade', 'Cidade'],
                ['personalizarNome', 'Nome']
            ];
            for (var i = 0; i < camposPersonalizacao.length; i++) {
                var campo = document.getElementById(camposPersonalizacao[i][0]);
                if (campo && !String(campo.value || '').trim()) {
                    return avisoPbdoc("Preencha o campo '" + camposPersonalizacao[i][1] + "' antes de gravar o documento.", silencioso, campo);
                }
            }
        }

        if (typeof window.validarCamposEntrevista === 'function') {
            window.validarCamposEntrevista();
            limparFavorPreencherInline();
        }

        var camposInvalidos = $('#frm').find('.is-invalid').not('input[type="hidden"]').filter(':visible');
        if (camposInvalidos.length) {
            var nome = nomeCampoInvalido(camposInvalidos[0]);
            if (nome) {
                return avisoPbdoc("Preencha o campo '" + nome + "' antes de gravar o documento.", silencioso, camposInvalidos[0]);
            }
            return avisoPbdoc('Favor verificar o campo destacado', silencioso, camposInvalidos[0]);
        }

        var eletroHidden = document.getElementById('eletronicoHidden');
        var eletro1 = document.getElementById('eletronicoCheck1');
        var eletro2 = document.getElementById('eletronicoCheck2');
        if (!eletroHidden && eletro1 && eletro2 && !eletro1.checked && !eletro2.checked) {
            return avisoPbdoc('É necessário informar se o documento será digital ou físico, na parte superior da tela.', silencioso, eletro1);
        }

        var limiteEl = byName('exDocumentoDTO.tamanhoMaximoDescricao');
        if (limiteEl && descr && descr.value.length >= Number(limiteEl.value || 0)) {
            return avisoPbdoc('O tamanho máximo da descrição é de ' + limiteEl.value + ' caracteres', silencioso, descr);
        }

        var personalizacaoJunta = document.getElementById('frm_nmFuncaoSubscritor');
        if (personalizacaoJunta && personalizacaoJunta.value.length > 128) {
            return avisoPbdoc('O tamanho máximo da soma dos caracteres de personalização é de 128 caracteres', silencioso, personalizacaoJunta);
        }

        return true;
    }

    function gravarPbdoc(assinar) {
        if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
        if (!validarPbdoc(false)) {
            if (typeof window.triggerAutoSave === 'function') window.triggerAutoSave();
            if (window.sigaSpinner && typeof window.sigaSpinner.ocultar === 'function') window.sigaSpinner.ocultar();
            return false;
        }

        var frm = document.getElementById('frm');
        if (!frm) return false;

        frm.action = 'gravar';
        window.customOnsubmit = function() { return true; };
        if (typeof frm.submitsave !== 'undefined') frm.submit = frm.submitsave;
        if (typeof window.onSave === 'function') window.onSave();

        var gravarAssinar = document.getElementById('gravarAssinar');
        if (gravarAssinar) gravarAssinar.value = assinar ? 'true' : 'false';
        var fecharDoc = document.getElementById('fecharDoc');
        if (fecharDoc) fecharDoc.value = assinar ? 'true' : 'false';

        var btn = document.getElementById(assinar ? 'btnFinalizarAssinar' : 'btnGravar');
        if (btn) btn.disabled = true;
        if (assinar && window.sigaSpinner && typeof window.sigaSpinner.mostrar === 'function') window.sigaSpinner.mostrar();

        frm.submit();
        return false;
    }

    function styleButtonsLikePBdoc() {
        var buttons = [
            document.getElementById('btnGravar'),
            document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]'),
            document.querySelector('button[name="ver_doc"]'),
            document.querySelector('button[name="ver_doc_pdf"]'),
            document.querySelector('button[name="voltar"]')
        ].filter(Boolean);
        if (!buttons.length) return;

        var parent = buttons[0].parentNode;
        if (parent) {
            parent.style.display = 'flex';
            parent.style.flexWrap = 'wrap';
            parent.style.alignItems = 'center';
            parent.style.gap = '3px';
        }
        buttons.forEach(function(btn) { btn.style.margin = '0'; });

        var gravar = document.getElementById('btnGravar');
        if (gravar) {
            gravar.className = 'btn btn-primary';
            gravar.innerHTML = '<u>G</u>ravar';
            gravar.onclick = function(e) { if (e) e.preventDefault(); return gravarPbdoc(false); };
        }

        var finalizar = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
        if (finalizar) {
            finalizar.id = 'btnFinalizarAssinar';
            finalizar.className = 'btn btn-primary';
            finalizar.innerHTML = '<u>F</u>inalizar e Assinar';
            finalizar.onclick = function(e) { if (e) e.preventDefault(); return gravarPbdoc(true); };
        }

        var verDoc = document.querySelector('button[name="ver_doc"]');
        if (verDoc) { verDoc.className = 'btn btn-info'; verDoc.innerHTML = '<u>V</u>er Documento'; }
        var verPdf = document.querySelector('button[name="ver_doc_pdf"]');
        if (verPdf) { verPdf.className = 'btn btn-info'; verPdf.innerHTML = 'Ver <u>I</u>mpressão'; }
        var voltar = document.querySelector('button[name="voltar"]');
        if (voltar) { voltar.className = 'btn btn-info'; voltar.innerHTML = 'Volta<u>r</u>'; }
    }

    function trocarMatriculaPorUsuario(root) {
        var $root = root ? $(root) : $(document);

        var tipoDest = $('select[name="exDocumentoDTO.tipoDestinatario"]');
        tipoDest.find('option[value="1"]').each(function() {
            if (/matr[ií]cula/i.test($(this).text())) $(this).text('Usuário');
        });

        $root.find('th,td,label,span,div,a,option').addBack('th,td,label,span,div,a,option').each(function() {
            if (this.children && this.children.length) return;
            var txt = clean(this.textContent);
            if (/^Matr[ií]cula$/i.test(txt)) this.textContent = 'Usuário';
        });
    }

    function installRecipientObserver() {
        trocarMatriculaPorUsuario(document);
        if (!window.MutationObserver || !document.body) return;
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                for (var i = 0; i < m.addedNodes.length; i++) {
                    if (m.addedNodes[i].nodeType === 1) trocarMatriculaPorUsuario(m.addedNodes[i]);
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function install() {
        if (window.location.pathname.indexOf('/app/expediente/doc/editar') < 0) return;

        /* Sobrescreve o fluxo anterior e usa a mesma estrutura de validação do PBdoc. */
        window.validar = validarPbdoc;
        window.gravar = gravarPbdoc;
        window.gravarDoc = function() { return gravarPbdoc(false); };
        window.gravarAssinarDoc = function() { return gravarPbdoc(true); };

        styleButtonsLikePBdoc();
        installRecipientObserver();

        setTimeout(function() {
            styleButtonsLikePBdoc();
            trocarMatriculaPorUsuario(document);
        }, 300);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
    else install();
})(window, document, window.jQuery);
