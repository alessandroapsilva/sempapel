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

    function getQueryParam(name) {
        try {
            return new URL(window.location.href).searchParams.get(name) || '';
        } catch (e) {
            var m = new RegExp('[?&]' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^&#]*)').exec(window.location.search);
            return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
        }
    }

    function ensureHidden(frm, name, value) {
        if (!frm || !value) return null;
        var el = byName(name);
        if (!el) {
            el = document.createElement('input');
            el.type = 'hidden';
            el.name = name;
            frm.appendChild(el);
        }
        el.value = value;
        return el;
    }

    function preserveParentContext() {
        var frm = form();
        if (!frm) return '';

        var existing = byName('exDocumentoDTO.mobilPaiSel.sigla');
        var siglaPai = existing && existing.value ? existing.value : '';
        if (!siglaPai) siglaPai = getQueryParam('mobilPaiSel.sigla');
        if (!siglaPai) siglaPai = getQueryParam('exDocumentoDTO.mobilPaiSel.sigla');

        if (siglaPai) {
            ensureHidden(frm, 'exDocumentoDTO.mobilPaiSel.sigla', siglaPai);
            ensureHidden(frm, 'mobilPaiSel.sigla', siglaPai);
        }
        return siglaPai;
    }

    function installModelLoader() {
        if (typeof window.carregaModelos !== 'function' || !$ || !$.ajax) return;

        window.getListaModelos = function() {
            var siglaPai = preserveParentContext();
            var idModEl = byName('exDocumentoDTO.idMod');
            var isEditandoAnexoEl = byName('exDocumentoDTO.criandoAnexo');
            var isCriandoSubprocessoEl = byName('exDocumentoDTO.criandoSubprocesso');
            var isAutuandoEl = byName('exDocumentoDTO.autuando');
            var isEditandoAnexo = !!(isEditandoAnexoEl && isEditandoAnexoEl.value === 'true');
            var isCriandoSubprocesso = !!(isCriandoSubprocessoEl && isCriandoSubprocessoEl.value === 'true');
            var isAutuando = !!(isAutuandoEl && isAutuandoEl.value === 'true');
            var ulMod = $('#ulmod');
            var selected = $('#modelos-select .selected-label');

            ulMod.empty();
            selected.empty().append('<span id="select-spinner" class="spinner-border spinner-border-sm text-secondary" role="status" aria-hidden="true"></span><span class="disabled ml-2">Carregando...</span>');

            var parts = [];
            if (isEditandoAnexo) parts.push('isEditandoAnexo=true');
            if (isCriandoSubprocesso) parts.push('isCriandoSubprocesso=true');
            if (isAutuando) parts.push('isAutuando=true');
            if (siglaPai) parts.push('siglaMobPai=' + encodeURIComponent(siglaPai));
            if (idModEl && idModEl.value) parts.push('idMod=' + encodeURIComponent(idModEl.value));
            var qry = parts.join('&');

            $.ajax({
                url: '/sigaex/api/v1/modelos/lista-hierarquica' + (qry ? '?' + qry : ''),
                contentType: 'application/json',
                dataType: 'json',
                timeout: 15000,
                success: function(result) {
                    if (result && result.list && result.list.length > 0) {
                        try {
                            if (typeof window.setUserSessionStorage === 'function') {
                                window.setUserSessionStorage('lastQry', qry);
                                window.setUserSessionStorage('modelos', JSON.stringify(result.list));
                            }
                        } catch (e) {}
                        window.carregaModelos(ulMod, result.list);
                    } else {
                        selected.html('&nbsp;');
                    }
                },
                error: function() {
                    selected.html('&nbsp;');
                },
                complete: function() {
                    $('#select-spinner').remove();
                    selected.find('.disabled').remove();
                }
            });
        };
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
            if (typeof window.validarCamposObrigatoriosEditaDocumento === 'function') window.validarCamposObrigatoriosEditaDocumento();
        } catch (e) { console.error(e); }
        try {
            if (typeof window.validarCamposEntrevista === 'function') window.validarCamposEntrevista();
        } catch (e) { console.error(e); }
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
            validateSelection(missing, 'exDocumentoDTO.titularSel.sigla', 'Substituto Responsável pela Assinatura');
        } else {
            clearInvalid(byName('exDocumentoDTO.titularSel.sigla'));
        }

        var tipoDest = byName('exDocumentoDTO.tipoDestinatario');
        if (tipoDest && visible(tipoDest)) {
            if (String(tipoDest.value) === '1') validateSelection(missing, 'exDocumentoDTO.destinatarioSel.sigla', 'Destinatário - Usuário');
            else if (String(tipoDest.value) === '2') validateSelection(missing, 'exDocumentoDTO.lotacaoDestinatarioSel.sigla', 'Destinatário - Lotação');
            else if (String(tipoDest.value) === '3') validateSelection(missing, 'exDocumentoDTO.orgaoExternoDestinatarioSel.sigla', 'Destinatário - Órgão Externo');
            else validateInput(missing, byName('exDocumentoDTO.nmDestinatario'), 'Destinatário - Campo Livre');
        }

        validateSelection(missing, 'exDocumentoDTO.classificacaoSel.sigla', 'Tipo Documental');
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

    function showRequiredModal(fields) {
        if (!fields || !fields.length) return;

        var nomeCampo = fields[0];
        var msg = "Preencha o campo '" + nomeCampo + "' antes de gravar o documento.";
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
        try { if (window.sigaSpinner && window.sigaSpinner.ocultar) window.sigaSpinner.ocultar(); } catch (e) {}
    }

    function showSpinner() {
        try { if (window.sigaSpinner && window.sigaSpinner.mostrar) window.sigaSpinner.mostrar(); } catch (e) {}
    }

    function syncEditor() {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            Object.keys(window.CKEDITOR.instances).forEach(function(key) { window.CKEDITOR.instances[key].updateElement(); });
        }
        if (typeof window.onSave === 'function') window.onSave();
        if (typeof window.personalizacaoJuntar === 'function') window.personalizacaoJuntar();
        preserveParentContext();
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
                showRequiredModal(missing);
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

    window.exibirModalCamposObrigatoriosDocumento = function(mensagens) {
        var nomes = [];
        (mensagens || []).forEach(function(mensagem) {
            var nome = clean(String(mensagem || '')
                .replace(/^Favor\s+(preencher|informar|selecionar)\s+(o\s+|a\s+)?campo\s*/i, '')
                .replace(/^Preencha\s+(o\s+|a\s+)?campo\s*/i, '')
                .replace(/\s+antes\s+de\s+gravar\s+o\s+documento\.?$/i, '')
                .replace(/[.'\"]+$/g, ''));
            if (nome && nomes.indexOf(nome) < 0) nomes.push(nome);
        });
        showRequiredModal(nomes.length ? nomes : collectMissingFields());
    };

    function styleButtonsLikePBdoc() {
        var gravar = document.getElementById('btnGravar');
        if (gravar) {
            gravar.className = 'btn btn-primary';
            gravar.innerHTML = '<u>G</u>ravar';
            gravar.title = 'Apenas grava o documento podendo continuar a Edição';
            gravar.style.cssText = '';
        }

        var finalizar = document.getElementById('btnFinalizarAssinar');
        if (finalizar) {
            finalizar.className = 'btn btn-primary';
            finalizar.innerHTML = '<u>F</u>inalizar e Assinar';
            finalizar.title = 'Finalizar documento em definitivo e em seguida realizar assinatura digital';
            finalizar.style.cssText = '';
        }

        var verDoc = document.querySelector('button[name="ver_doc"]');
        if (verDoc) {
            verDoc.className = 'btn btn-info';
            verDoc.innerHTML = '<u>V</u>er Documento';
            verDoc.style.cssText = '';
        }

        var verPdf = document.querySelector('button[name="ver_doc_pdf"]');
        if (verPdf) {
            verPdf.className = 'btn btn-info';
            verPdf.innerHTML = 'Ver <u>I</u>mpressão';
            verPdf.style.cssText = '';
        }

        var voltar = document.querySelector('button[name="voltar"]');
        if (voltar) {
            voltar.className = 'btn btn-info';
            voltar.innerHTML = 'Volta<u>r</u>';
            voltar.style.cssText = '';
        }
    }

    function installExibeActions() {
        if (window.location.pathname.indexOf('/app/expediente/doc/exibir') < 0) return;

        /* Remove somente o Voltar do cabeçalho do exibe.jsp. */
        var voltarCabecalho = document.querySelector('#page h2 button[name="voltar"], #page h2.sigla-documento button[name="voltar"]');
        if (voltarCabecalho) voltarCabecalho.parentNode.removeChild(voltarCabecalho);

        /*
         * O PBdoc já entrega Anexar pelas ações permitidas do móbil. Em vez de
         * inventar uma rota e furar a regra de negócio, reaproveitamos exatamente
         * a ação autorizada e apenas a promovemos para um botão visível.
         */
        var menus = document.querySelectorAll('.siga-menu-acoes');
        for (var i = 0; i < menus.length; i++) {
            var menu = menus[i];
            if (menu.querySelector('.enfas-btn-anexar')) continue;

            var links = menu.querySelectorAll('a[href]');
            var anexarOriginal = null;
            for (var j = 0; j < links.length; j++) {
                var href = links[j].getAttribute('href') || '';
                var texto = clean(links[j].textContent || '');
                if (href.indexOf('/app/expediente/mov/anexar') >= 0 || /^Anexar$/i.test(texto)) {
                    anexarOriginal = links[j];
                    break;
                }
            }

            if (!anexarOriginal) continue;

            var botao = document.createElement('a');
            botao.className = 'btn btn-primary btn-sm enfas-btn-anexar mr-2 mb-2';
            botao.href = anexarOriginal.href;
            botao.title = anexarOriginal.title || 'Anexar documento';
            botao.innerHTML = '<u>A</u>nexar';

            var col = menu.querySelector('.col') || menu;
            var referencia = col.querySelector('h3');
            if (referencia && referencia.nextSibling) col.insertBefore(botao, referencia.nextSibling);
            else col.insertBefore(botao, col.firstChild);

            /* Evita exibir a mesma ação duas vezes. */
            var li = anexarOriginal.closest ? anexarOriginal.closest('li') : null;
            if (li) li.style.display = 'none';
            else anexarOriginal.style.display = 'none';
        }
    }

    function install() {
        var frm = form();
        if (frm) window.frm = frm;

        preserveParentContext();
        styleButtonsLikePBdoc();
        installExibeActions();

        var gravar = document.getElementById('btnGravar');
        if (gravar) gravar.onclick = function(e) { if (e) e.preventDefault(); return submitDocument(false); };

        var finalizar = document.getElementById('btnFinalizarAssinar');
        if (finalizar) finalizar.onclick = function(e) { if (e) e.preventDefault(); return submitDocument(true); };
    }

    preserveParentContext();
    installModelLoader();

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
    else install();
})(window, document, window.jQuery);