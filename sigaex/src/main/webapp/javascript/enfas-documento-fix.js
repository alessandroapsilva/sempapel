(function(window, document, $) {
    'use strict';

    function form() { return document.getElementById('frm'); }
    function byName(name) { var a = document.getElementsByName(name); return a && a.length ? a[0] : null; }
    function clean(s) { return String(s || '').replace(/\*/g, '').replace(/\s+/g, ' ').trim(); }
    function fieldLabel(el, fallback) {
        if (!el) return fallback || 'Campo obrigatorio';
        var t = $(el).closest('.form-group').find('label').first().clone().children().remove().end().text();
        return clean(t) || fallback || 'Campo obrigatorio';
    }
    function visible(el) { return !!el && !$(el).is(':disabled') && !$(el).closest('.d-none,[hidden],[style*="display: none"]').length; }
    function valueSelection(name) {
        var id = byName(name.replace('Sel.sigla', 'Sel.id'));
        var el = byName(name);
        return id && id.value ? id.value : (el ? el.value : '');
    }
    function mark(el, bad) { if (el) $(el).toggleClass('is-invalid', !!bad); }

    function conditionalRequired() {
        var list = [];
        function selection(name, fallback) {
            var el = byName(name);
            if (!visible(el)) return;
            var bad = !String(valueSelection(name) || '').trim();
            mark(el, bad);
            if (bad) {
                var n = fieldLabel(el, fallback);
                if (list.indexOf(n) < 0) list.push(n);
            }
        }
        function inputId(id, fallback) {
            var el = document.getElementById(id);
            if (!visible(el)) return;
            var bad = !String(el.value || '').trim();
            mark(el, bad);
            if (bad && list.indexOf(fallback) < 0) list.push(fallback);
        }

        if ($('#substitutoSwitch').is(':checked')) selection('exDocumentoDTO.titularSel.sigla', 'Substituto do Responsavel pela Assinatura');
        else mark(byName('exDocumentoDTO.titularSel.sigla'), false);

        if ($('#cossignatariosSwitch').is(':checked')) selection('exDocumentoDTO.cosignatarioSel.sigla', 'Outros Assinantes / Cossignatarios');

        if ($('#personalizacaoSwitch').is(':checked')) {
            inputId('personalizarFuncao', 'Funcao');
            inputId('personalizarUnidade', 'Lotacao');
            inputId('personalizarLocalidade', 'Cidade');
            inputId('personalizarNome', 'Nome');
        }
        return list;
    }

    function modal(fields, finalizar) {
        var titulo = finalizar ? 'Campos obrigatorios para finalizar e assinar:' : 'Campos obrigatorios para gravar:';
        var msg = titulo + '\n\n' + fields.map(function(x) { return '• ' + x; }).join('\n');
        var first = $('#frm .is-invalid:visible').first()[0] || null;
        if (window.sigaModal && window.sigaModal.alerta) {
            var m = window.sigaModal.alerta(msg);
            if (m && m.focus) m.focus(first);
        } else window.alert(msg);
    }

    /* Modal nativo do SIGA: somente nomes reais dos campos, sem "Favor preencher...". */
    window.obterMensagemCampoInvalidoDocumento = function(elemento) {
        return fieldLabel(elemento && elemento.jquery ? elemento[0] : elemento);
    };
    window.obterMensagensCamposInvalidosDocumento = function() {
        var list = [];
        $('#frm .is-invalid:visible').each(function() {
            if (this.type === 'hidden') return;
            var n = fieldLabel(this);
            if (list.indexOf(n) < 0) list.push(n);
        });
        return list;
    };
    window.exibirModalCamposObrigatoriosDocumento = function(mensagens, finalizar) { modal(mensagens || [], finalizar); };

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
        if (missing.length) { hideSpinner(); modal(missing, finalizar); return false; }
        if (typeof window.validar === 'function' && !window.validar(false, finalizar)) { hideSpinner(); return false; }
        return true;
    }
    function prepare(frm) {
        window.frm = frm;
        window.customOnsubmit = function() { return true; };
        if (typeof frm.submitsave !== 'undefined') frm.submit = frm.submitsave;
    }

    window.gravarDoc = function() {
        var frm = form();
        if (!frm) return false;
        try {
            if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
            syncEditor();
            if (!validate(false)) { if (window.triggerAutoSave) window.triggerAutoSave(); return false; }
            var a = document.getElementById('gravarAssinar');
            var f = document.getElementById('fecharDoc');
            if (a) a.value = 'false';
            if (f) f.value = 'false';
            prepare(frm);
            frm.action = 'gravar';
            var b = document.getElementById('btnGravar');
            if (b) b.disabled = true;
            frm.submit();
        } catch (e) {
            var b2 = document.getElementById('btnGravar');
            if (b2) b2.disabled = false;
            hideSpinner();
            if (window.sigaModal) window.sigaModal.alerta('Erro ao gravar o documento.');
            console.error(e);
        }
        return false;
    };

    window.gravarAssinarDoc = function() {
        var frm = form();
        if (!frm) return false;
        try {
            if (typeof window.saveTimer !== 'undefined') clearTimeout(window.saveTimer);
            syncEditor();
            /* O spinner aparece apenas depois de toda validacao terminar. */
            if (!validate(true)) { if (window.triggerAutoSave) window.triggerAutoSave(); return false; }
            var a = document.getElementById('gravarAssinar');
            var f = document.getElementById('fecharDoc');
            if (!a || !f) throw new Error('Campos de finalizacao ausentes');
            a.value = 'true';
            f.value = 'true';
            prepare(frm);
            frm.action = 'gravar';
            var b = document.getElementById('btnFinalizarAssinar');
            if (b) b.disabled = true;
            showSpinner();
            frm.submit();
        } catch (e) {
            var b2 = document.getElementById('btnFinalizarAssinar');
            if (b2) b2.disabled = false;
            hideSpinner();
            if (window.sigaModal) window.sigaModal.alerta('Erro ao finalizar e assinar o documento.');
            console.error(e);
        }
        return false;
    };

    function install() {
        var frm = form();
        if (frm) window.frm = frm;
        var g = document.getElementById('btnGravar');
        if (g) g.onclick = function(e) { if (e) e.preventDefault(); return window.gravarDoc(); };
        var f = document.getElementById('btnFinalizarAssinar');
        if (f) f.onclick = function(e) { if (e) e.preventDefault(); return window.gravarAssinarDoc(); };
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
})(window, document, window.jQuery);
