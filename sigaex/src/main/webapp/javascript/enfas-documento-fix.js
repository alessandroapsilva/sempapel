(function(window, document, $) {
    'use strict';

    function form() {
        return document.getElementById('frm');
    }

    function byName(name) {
        var els = document.getElementsByName(name);
        return els && els.length ? els[0] : null;
    }

    function clean(text) {
        return String(text || '')
            .replace(/\(obrigat[oó]rio\)/ig, '')
            .replace(/\*/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function visible(el) {
        if (!el || $(el).is(':disabled')) return false;
        if ($(el).closest('.d-none,[hidden]').length) return false;
        var parentWithStyle = $(el).closest('[style]');
        if (parentWithStyle.length && /display\s*:\s*none/i.test(parentWithStyle.attr('style') || '')) return false;
        return true;
    }

    function fieldName(el, fallback) {
        if (!el) return fallback || 'Campo obrigatório';
        var group = $(el).closest('.form-group');
        var label = group.find('label').first().clone();
        label.find('a,span,i,small').remove();
        var text = clean(label.text());
        return text || fallback || clean(el.getAttribute('title')) || 'Campo obrigatório';
    }

    function selectionValue(siglaName) {
        var sigla = byName(siglaName);
        var id = byName(siglaName.replace('Sel.sigla', 'Sel.id'));
        if (id && String(id.value || '').trim()) return id.value;
        return sigla ? sigla.value : '';
    }

    function addMissing(list, el, fallback) {
        var name = fallback || fieldName(el, fallback);
        if (name && list.indexOf(name) < 0) list.push(name);
        if (el) $(el).addClass('is-invalid');
    }

    function clearInvalid(el) {
        if (el) $(el).removeClass('is-invalid');
    }

    function validateSelection(list, name, fallback) {
        var el = byName(name);
        if (!el || !visible(el)) return;
        if (!String(selectionValue(name) || '').trim()) addMissing(list, el, fallback);
        else clearInvalid(el);
    }

    function validateInput(list, el, fallback) {
        if (!el || !visible(el)) return;
        if (!String(el.value || '').trim()) addMissing(list, el, fallback);
        else clearInvalid(el);
    }

    function runSigaFieldValidation() {
        try {
            if (typeof window.validarCamposObrigatoriosEditaDocumento === 'function') {
                window.validarCamposObrigatoriosEditaDocumento();
            }
        } catch (e) {
            console.error(e);
        }
        try {
            if (typeof window.validarCamposEntrevista === 'function') {
                window.validarCamposEntrevista();
            }
        } catch (e) {
            console.error(e);
        }
    }

    function collectMissingFields() {
        runSigaFieldValidation();
        var missing = [];

        $('#frm').find('.is-invalid').each(function() {
            if (this.type === 'hidden' || !visible(this)) return;
            addMissing(missing, this);
        });

        validateSelection(missing, 'exDocumentoDTO.subscritorSel.sigla', 'Responsável pela Assinatura');

        var substituto = document.getElementById('substitutoSwitch') || byName('exDocumentoDTO.substituicao');
        if (substituto && substituto.checked) {
            validateSelection(missing, 'exDocumentoDTO.titularSel.sigla', 'Titular');
        } else {
            clearInvalid(byName('exDocumentoDTO.titularSel.sigla'));
        }

        var tipoDest = byName('exDocumentoDTO.tipoDestinatario');
        if (tipoDest && visible(tipoDest)) {
            if (String(tipoDest.value) === '1') {
                validateSelection(missing, 'exDocumentoDTO.destinatarioSel.sigla', 'Destinatário - Pessoa');
            } else if (String(tipoDest.value) === '2') {
                validateSelection(missing, 'exDocumentoDTO.lotacaoDestinatarioSel.sigla', 'Destinatário - Lotação');
            } else if (String(tipoDest.value) === '3') {
                validateSelection(missing, 'exDocumentoDTO.orgaoExternoDestinatarioSel.sigla', 'Destinatário - Órgão Externo');
            } else {
                validateInput(missing, byName('exDocumentoDTO.nmDestinatario'), 'Destinatário');
            }
        }

        validateSelection(missing, 'exDocumentoDTO.classificacaoSel.sigla', 'Classificação Documental');
        validateInput(missing, byName('exDocumentoDTO.descrDocumento'), 'Assunto');

        var personalizar = document.getElementById('personalizacaoSwitch') || byName('exDocumentoDTO.personalizacao');
        if (personalizar && personalizar.checked) {
            validateInput(missing, document.getElementById('personalizarFuncao'), 'Função');
            validateInput(missing, document.getElementById('personalizarUnidade'), 'Lotação');
            validateInput(missing, document.getElementById('personalizarLocalidade'), 'Cidade');
            validateInput(missing, document.getElementById('personalizarNome'), 'Nome');
        }

        var cossignatarios = document.getElementById('cossignatariosSwitch');
        if (cossignatarios && cossignatarios.checked) {
            validateSelection(missing, 'exDocumentoDTO.cosignatarioSel.sigla', 'Outros Assinantes / Cossignatários');
        }

        $('#frm').find('[required],[aria-required="true"]').each(function() {
            if (this.type === 'hidden' || !visible(this)) return;
            if ((this.type === 'checkbox' || this.type === 'radio')) {
                if (!$('[name="' + this.name + '"]:checked').length) addMissing(missing, this);
            } else if (!String($(this).val() || '').trim()) {
                addMissing(missing, this);
            }
        });

        return missing;
    }

    function showRequiredModal(fields, finalizar) {
        if (!fields || !fields.length) return;

        /* Igual ao PBdoc: mostra o primeiro campo pendente com frase completa. */
        var nomeCampo = fields[0];
        var acao = finalizar ? 'finalizar e assinar o documento' : 'gravar o documento';
        var msg = "Preencha o campo '" + nomeCampo + "' antes de " + acao + ".";

        var first = $('#frm .is-invalid:visible').first()[0] || null;
        if (window.sigaModal && typeof window.sigaModal.alerta === 'function') {
            var modal = window.sigaModal.alerta(msg);
            if (modal && typeof modal.focus === 'function') modal.focus(first);
        } else {
            window.alert(msg);
            if (first && first.focus) first.focus();
        }
    }

    function hideSpinner() {
        try {
            if (window.sigaSpinner && window.sigaSpinner.ocultar) window.sigaSpinner.ocultar();
        } catch (e) {}
    }

    function showSpinner() {
        try {
            if (window.sigaSpinner && window.sigaSpinner.mostrar) window.sigaSpinner.mostrar();
        } catch (e) {}
    }

    function syncEditor() {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            Object.keys(window.CKEDITOR.instances).forEach(function(key) {
                window.CKEDITOR.instances[key].updateElement();
            });
        }
        if (typeof window.onSave === 'function') window.onSave();
        if (typeof window.personalizacaoJuntar === 'function') window.personalizacaoJuntar();
    }

    function nativeSubmit(frm) {
        window.customOnsubmit = function() { return true; };
        frm.onsubmit = null;
        HTMLFormElement.prototype.submit.call(frm);
    }

    function submitDocument(finalizar) {
        var frm = form();
        if (!frm) return false;

        hideSpinner();
        try {
            if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
            syncEditor();

            var missing = collectMissingFields();
            if (missing.length) {
                showRequiredModal(missing, finalizar);
                if (typeof window.triggerAutoSave === 'function') window.triggerAutoSave();
                return false;
            }

            var assinar = document.getElementById('gravarAssinar');
            var fechar = document.getElementById('fecharDoc');
            if (assinar) assinar.value = finalizar ? 'true' : 'false';
            if (fechar) fechar.value = finalizar ? 'true' : 'false';

            frm.action = 'gravar';

            var button = document.getElementById(finalizar ? 'btnFinalizarAssinar' : 'btnGravar');
            if (button) button.disabled = true;

            if (finalizar) showSpinner();
            nativeSubmit(frm);
        } catch (e) {
            hideSpinner();
            var button2 = document.getElementById(finalizar ? 'btnFinalizarAssinar' : 'btnGravar');
            if (button2) button2.disabled = false;
            console.error('Falha no envio do edita.jsp', e);
        }
        return false;
    }

    window.gravarDoc = function() { return submitDocument(false); };
    window.gravarAssinarDoc = function() { return submitDocument(true); };

    /* Compatibilidade com a validacao original: qualquer chamada ao resumo usa o mesmo modal PBdoc. */
    window.exibirModalCamposObrigatoriosDocumento = function(mensagens, finalizar) {
        var nomes = [];
        (mensagens || []).forEach(function(mensagem) {
            var nome = clean(String(mensagem || '')
                .replace(/^Favor\s+(preencher|informar|selecionar)\s+(o\s+|a\s+)?campo\s*/i, '')
                .replace(/^Preencha\s+(o\s+|a\s+)?campo\s*/i, '')
                .replace(/[.'\"]+$/g, ''));
            if (nome && nomes.indexOf(nome) < 0) nomes.push(nome);
        });
        showRequiredModal(nomes.length ? nomes : collectMissingFields(), !!finalizar);
    };

    function install() {
        var frm = form();
        if (frm) window.frm = frm;

        var gravar = document.getElementById('btnGravar');
        if (gravar) {
            gravar.onclick = function(e) {
                if (e) e.preventDefault();
                return submitDocument(false);
            };
        }

        var finalizar = document.getElementById('btnFinalizarAssinar');
        if (finalizar) {
            finalizar.onclick = function(e) {
                if (e) e.preventDefault();
                return submitDocument(true);
            };
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install);
    } else {
        install();
    }
})(window, document, window.jQuery);
