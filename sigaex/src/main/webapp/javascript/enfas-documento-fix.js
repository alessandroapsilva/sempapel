/*
 * Correções ENFAS para o fluxo de edição do SIGA-EX.
 *
 * Este arquivo é carregado no rodapé das páginas do /sigaex para garantir
 * que as implementações abaixo prevaleçam sobre funções duplicadas em JSPs
 * antigos/customizados.
 */
(function(window, document, $) {
    'use strict';

    function getForm() {
        return document.getElementById('frm');
    }

    function getFirstByName(name) {
        var elements = document.getElementsByName(name);
        return elements && elements.length ? elements[0] : null;
    }

    function getValue(name) {
        var el = getFirstByName(name);
        return el ? (el.value || '') : '';
    }

    function hideSpinner() {
        try {
            if (typeof window.sigaSpinner !== 'undefined' && window.sigaSpinner.ocultar) {
                window.sigaSpinner.ocultar();
            }
        } catch (e) {
            // Não deixa erro de spinner interromper o fluxo principal.
        }
    }

    function showError(message, error) {
        hideSpinner();
        try {
            console.error(message, error || '');
        } catch (e) {}

        if (typeof window.sigaModal !== 'undefined' && typeof window.sigaModal.alerta === 'function') {
            window.sigaModal.alerta(message);
        } else {
            window.alert(message);
        }
    }

    function prepareSubmit(form) {
        window.customOnsubmit = function() {
            return true;
        };

        if (typeof form.submitsave !== 'undefined') {
            form.submit = form.submitsave;
        }

        if (typeof window.onSave === 'function') {
            window.onSave();
        }
    }

    function submitForm(form) {
        if (!form) {
            throw new Error('Formulário de documento não encontrado.');
        }
        form.submit();
    }

    /*
     * Corrige o recarregamento da edição. Havia uma implementação no edita.jsp
     * comparando o valor de id com a string "undefined", fazendo sbmt() sem
     * parâmetro cair indevidamente em "recarregar" e perdendo contexto de
     * modelo/anexo/subprocesso.
     */
    window.sbmt = function(id) {
        var form = getForm();
        if (!form) {
            return false;
        }

        var mod = getFirstByName('exDocumentoDTO.idMod');
        if (mod && mod.value === '[Selecione]') {
            mod.value = '0';
        }

        try {
            if (typeof window.onSave === 'function') {
                window.onSave();
            }

            if (id && typeof window.IsRunningAjaxRequest === 'function'
                    && !window.IsRunningAjaxRequest()
                    && typeof window.ReplaceInnerHTMLFromAjaxResponse === 'function') {
                window.ReplaceInnerHTMLFromAjaxResponse('recarregar', form, id);
                return false;
            }

            var paiSigla = getValue('exDocumentoDTO.mobilPaiSel.sigla');
            var criandoAnexo = getValue('exDocumentoDTO.criandoAnexo');
            var criandoSubprocesso = getValue('exDocumentoDTO.criandoSubprocesso');
            var autuando = getValue('exDocumentoDTO.autuando');
            var modelo = mod ? mod.value : '0';

            var query = 'modelo=' + encodeURIComponent(modelo || '0');
            if (paiSigla) {
                query += '&mobilPaiSel.sigla=' + encodeURIComponent(paiSigla);
            }
            if (criandoAnexo) {
                query += '&criandoAnexo=' + encodeURIComponent(criandoAnexo);
            }
            if (criandoSubprocesso) {
                query += '&criandoSubprocesso=' + encodeURIComponent(criandoSubprocesso);
            }
            if (autuando) {
                query += '&autuando=' + encodeURIComponent(autuando);
            }

            form.action = id ? 'recarregar' : 'editar?' + query;
            submitForm(form);
        } catch (e) {
            showError('Não foi possível recarregar os dados do documento.', e);
        }
        return false;
    };

    window.gravarDoc = function() {
        var form = getForm();
        if (!form) {
            showError('Não foi possível localizar o formulário do documento.');
            return false;
        }

        try {
            if (typeof window.saveTimer !== 'undefined') {
                clearTimeout(window.saveTimer);
            }

            if (typeof window.validar === 'function' && !window.validar(false, false)) {
                if (typeof window.triggerAutoSave === 'function') {
                    window.triggerAutoSave();
                }
                hideSpinner();
                return false;
            }

            var assinar = document.getElementById('gravarAssinar');
            var fechar = document.getElementById('fecharDoc');
            if (assinar) assinar.value = 'false';
            if (fechar) fechar.value = 'false';

            form.action = 'gravar';
            prepareSubmit(form);

            var btn = document.getElementById('btnGravar');
            if (btn) btn.disabled = true;

            submitForm(form);
        } catch (e) {
            var btnGravar = document.getElementById('btnGravar');
            if (btnGravar) btnGravar.disabled = false;
            showError('Não foi possível gravar o documento. Verifique os campos e tente novamente.', e);
        }
        return false;
    };

    window.gravarAssinarDoc = function() {
        var form = getForm();
        if (!form) {
            showError('Não foi possível localizar o formulário do documento.');
            return false;
        }

        try {
            if (typeof window.sigaSpinner !== 'undefined' && window.sigaSpinner.mostrar) {
                window.sigaSpinner.mostrar();
            }

            if (typeof window.saveTimer !== 'undefined') {
                clearTimeout(window.saveTimer);
            }

            if (typeof window.validar === 'function' && !window.validar(false, true)) {
                if (typeof window.triggerAutoSave === 'function') {
                    window.triggerAutoSave();
                }
                hideSpinner();
                return false;
            }

            var assinar = document.getElementById('gravarAssinar');
            var fechar = document.getElementById('fecharDoc');
            if (!assinar || !fechar) {
                throw new Error('Campos de controle de finalização não encontrados.');
            }

            assinar.value = 'true';
            fechar.value = 'true';
            form.action = 'gravar';
            prepareSubmit(form);

            var btn = document.getElementById('btnFinalizarAssinar');
            if (btn) btn.disabled = true;

            submitForm(form);
        } catch (e) {
            var btnFinalizar = document.getElementById('btnFinalizarAssinar');
            if (btnFinalizar) btnFinalizar.disabled = false;
            showError('Não foi possível finalizar e assinar o documento.', e);
        }
        return false;
    };

    /*
     * Mantém o formulário de inclusão de documento/anexo com o contexto do pai.
     * O link "Incluir Documento" leva para /doc/editar com criandoAnexo=true;
     * esta proteção impede que uma recarga de modelo descarte esses parâmetros.
     */
    function preserveParentContext() {
        var form = getForm();
        if (!form) return;

        var params;
        try {
            params = new URLSearchParams(window.location.search || '');
        } catch (e) {
            return;
        }

        var mappings = [
            ['mobilPaiSel.sigla', 'exDocumentoDTO.mobilPaiSel.sigla'],
            ['criandoAnexo', 'exDocumentoDTO.criandoAnexo'],
            ['criandoSubprocesso', 'exDocumentoDTO.criandoSubprocesso'],
            ['autuando', 'exDocumentoDTO.autuando']
        ];

        mappings.forEach(function(mapping) {
            var value = params.get(mapping[0]);
            var field = getFirstByName(mapping[1]);
            if (value !== null && field && !field.value) {
                field.value = value;
            }
        });
    }

    function installFixes() {
        preserveParentContext();

        var btnGravar = document.getElementById('btnGravar');
        if (btnGravar) {
            btnGravar.onclick = function(e) {
                if (e) e.preventDefault();
                return window.gravarDoc();
            };
        }

        var btnFinalizar = document.getElementById('btnFinalizarAssinar');
        if (btnFinalizar) {
            btnFinalizar.onclick = function(e) {
                if (e) e.preventDefault();
                return window.gravarAssinarDoc();
            };
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installFixes);
    } else {
        installFixes();
    }
})(window, document, window.jQuery);
