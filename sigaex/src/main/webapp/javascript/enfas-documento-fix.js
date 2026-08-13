(function(window, document, $) {
    'use strict';

    function form() { return document.getElementById('frm'); }
    function byName(name) { var a = document.getElementsByName(name); return a && a.length ? a[0] : null; }
    function clean(s) {
        return String(s || '').replace(/\(obrigat[oó]rio\)/gi, '').replace(/\*/g, '').replace(/\s+/g, ' ').trim();
    }
    function visible(el) {
        return !!el && !$(el).is(':disabled') && !$(el).closest('.d-none,[hidden],[style*="display: none"]').length;
    }
    function fieldLabel(el, fallback) {
        if (!el) return fallback || '';
        var label = $(el).closest('.form-group').find('label').first();
        if (label.length) {
            var clone = label.clone();
            clone.find('i,a,small').remove();
            var text = clean(clone.text());
            if (text) return text;
        }
        return fallback || '';
    }
    function valueSelection(name) {
        var id = byName(name.replace('Sel.sigla', 'Sel.id'));
        var el = byName(name);
        return id && id.value ? id.value : (el ? el.value : '');
    }
    function mark(el, bad) { if (el) $(el).toggleClass('is-invalid', !!bad); }
    function addUnique(list, name) { name = clean(name); if (name && list.indexOf(name) < 0) list.push(name); }

    function conditionalRequired() {
        var list = [];
        function selection(name, fallback) {
            var el = byName(name);
            if (!visible(el)) return;
            var bad = !String(valueSelection(name) || '').trim();
            mark(el, bad);
            if (bad) addUnique(list, fieldLabel(el, fallback));
        }
        function inputId(id, fallback) {
            var el = document.getElementById(id);
            if (!visible(el)) return;
            var bad = !String(el.value || '').trim();
            mark(el, bad);
            if (bad) addUnique(list, fieldLabel(el, fallback));
        }

        var substituto = $('#substitutoSwitch, input[name="exDocumentoDTO.substituicao"]').first();
        if (substituto.length && substituto.is(':checked')) selection('exDocumentoDTO.titularSel.sigla', 'Titular');
        else mark(byName('exDocumentoDTO.titularSel.sigla'), false);

        var cossignatarios = $('#cossignatariosSwitch').first();
        if (cossignatarios.length && cossignatarios.is(':checked')) selection('exDocumentoDTO.cosignatarioSel.sigla', 'Outros Assinantes / Cossignatários');

        var personalizacao = $('#personalizacaoSwitch, input[name="exDocumentoDTO.personalizacao"]').first();
        if (personalizacao.length && personalizacao.is(':checked')) {
            inputId('personalizarFuncao', 'Função');
            inputId('personalizarUnidade', 'Lotação');
            inputId('personalizarLocalidade', 'Cidade');
            inputId('personalizarNome', 'Nome');
        }
        return list;
    }

    function currentInvalidNames() {
        var list = [];
        $('#frm .is-invalid').each(function() {
            if (this.type === 'hidden' || !visible(this)) return;
            addUnique(list, fieldLabel(this));
        });
        return list;
    }

    function normalizeNames(items) {
        var list = [];
        (items || []).forEach(function(item) {
            var name = clean(String(item || '')
                .replace(/^Favor\s+(preencher|informar|selecionar)\s+(o\s+|a\s+)?campo\s*/i, '')
                .replace(/^Favor\s+(preencher|informar|selecionar)\s*/i, '')
                .replace(/^[-•]\s*/, ''));
            addUnique(list, name);
        });
        return list;
    }

    /* Modal nativo do SIGA: somente nomes dos campos, como no PBdoc. */
    function modal(fields) {
        var names = normalizeNames(fields);
        currentInvalidNames().forEach(function(name) { addUnique(names, name); });
        conditionalRequired().forEach(function(name) { addUnique(names, name); });
        if (!names.length) return;

        var first = $('#frm .is-invalid').filter(function() {
            return this.type !== 'hidden' && visible(this);
        }).first()[0] || null;

        if (window.sigaModal && typeof window.sigaModal.alerta === 'function') {
            var m = window.sigaModal.alerta(names.join('<br>'));
            if (m && typeof m.focus === 'function') m.focus(first);
        } else {
            window.alert(names.join('\n'));
            if (first && typeof first.focus === 'function') first.focus();
        }
    }

    window.obterMensagemCampoInvalidoDocumento = function(elemento) {
        var el = elemento && elemento.jquery ? elemento[0] : elemento;
        return fieldLabel(el);
    };
    window.obterMensagensCamposInvalidosDocumento = function() { return currentInvalidNames(); };
    window.exibirModalCamposObrigatoriosDocumento = function(mensagens) { modal(mensagens || []); };

    function hideSpinner() { try { if (window.sigaSpinner && window.sigaSpinner.ocultar) window.sigaSpinner.ocultar(); } catch (e) {} }
    function showSpinner() { try { if (window.sigaSpinner && window.sigaSpinner.mostrar) window.sigaSpinner.mostrar(); } catch (e) {} }
    function syncEditor() {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            Object.keys(window.CKEDITOR.instances).forEach(function(k) { window.CKEDITOR.instances[k].updateElement(); });
        }
        if (typeof window.onSave === 'function') window.onSave();
    }
    function validate(finalizar) {
        var missing = conditionalRequired();
        if (missing.length) { hideSpinner(); modal(missing); return false; }
        if (typeof window.validar === 'function' && !window.validar(false, finalizar)) { hideSpinner(); return false; }
        return true;
    }
    function prepare(frm) {
        window.frm = frm;
        window.customOnsubmit = function() { return true; };
        if (typeof frm.submitsave !== 'undefined') frm.submit = frm.submitsave;
    }

    /* Botoes com o mesmo fluxo do PBdoc: validar e depois submeter. */
    window.gravarDoc = function() {
        var frm = form();
        if (!frm) return false;
        try {
            if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
            syncEditor();
            if (!validate(false)) { if (typeof window.triggerAutoSave === 'function') window.triggerAutoSave(); return false; }

            var assinar = document.getElementById('gravarAssinar');
            var fechar = document.getElementById('fecharDoc');
            if (assinar) assinar.value = 'false';
            if (fechar) fechar.value = 'false';

            prepare(frm);
            frm.action = 'gravar';
            var botao = document.getElementById('btnGravar');
            if (botao) botao.disabled = true;
            frm.submit();
        } catch (e) {
            var botaoErro = document.getElementById('btnGravar');
            if (botaoErro) botaoErro.disabled = false;
            hideSpinner();
            if (window.console && console.error) console.error(e);
        }
        return false;
    };

    window.gravarAssinarDoc = function() {
        var frm = form();
        if (!frm) return false;
        try {
            if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
            syncEditor();
            if (!validate(true)) { if (typeof window.triggerAutoSave === 'function') window.triggerAutoSave(); return false; }

            var assinar = document.getElementById('gravarAssinar');
            var fechar = document.getElementById('fecharDoc');
            if (assinar) assinar.value = 'true';
            if (fechar) fechar.value = 'true';

            prepare(frm);
            frm.action = 'gravar';
            var botao = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
            if (botao) botao.disabled = true;
            showSpinner();
            frm.submit();
        } catch (e) {
            var botaoErro = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
            if (botaoErro) botaoErro.disabled = false;
            hideSpinner();
            if (window.console && console.error) console.error(e);
        }
        return false;
    };

    function install() {
        var frm = form();
        if (frm) window.frm = frm;

        var gravar = document.getElementById('btnGravar');
        if (gravar) gravar.onclick = function(e) { if (e) e.preventDefault(); return window.gravarDoc(); };

        var finalizar = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
        if (finalizar) finalizar.onclick = function(e) { if (e) e.preventDefault(); return window.gravarAssinarDoc(); };
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
    else install();
})(window, document, window.jQuery);
