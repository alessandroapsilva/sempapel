(function(window, document, $) {
    'use strict';

    function label(el, fallback) {
        if (!el) return fallback || 'Campo obrigatorio';
        var t = $(el).closest('.form-group').find('label').first().clone().children().remove().end().text();
        t = String(t || '').replace(/\*/g, '').replace(/\s+/g, ' ').trim();
        return t || fallback || 'Campo obrigatorio';
    }

    function show(fields, finalizar) {
        var msg = (finalizar ? 'Campos obrigatorios para finalizar e assinar:' : 'Campos obrigatorios para gravar:') + '\n\n' + fields.map(function(x) { return '• ' + x; }).join('\n');
        var first = $('#frm .is-invalid:visible').first()[0] || null;
        var modal = window.sigaModal.alerta(msg);
        if (modal && modal.focus) modal.focus(first);
    }

    window.obterMensagemCampoInvalidoDocumento = function(elemento) {
        return label(elemento && elemento.jquery ? elemento[0] : elemento);
    };

    window.obterMensagensCamposInvalidosDocumento = function() {
        var out = [];
        $('#frm .is-invalid:visible').each(function() {
            if (this.type === 'hidden') return;
            var n = label(this);
            if (out.indexOf(n) < 0) out.push(n);
        });
        return out;
    };

    window.exibirModalCamposObrigatoriosDocumento = function(mensagens, finalizar) {
        show(mensagens || [], finalizar);
    };

    function ensureConditionalRequired() {
        var missing = [];
        function check(name, fallback) {
            var el = document.getElementsByName(name)[0];
            if (!el || $(el).is(':disabled') || $(el).closest('.d-none,[hidden],[style*="display: none"]').length) return;
            var id = document.getElementsByName(name.replace('Sel.sigla', 'Sel.id'))[0];
            var value = id && id.value ? id.value : el.value;
            if (!value || !String(value).trim()) {
                $(el).addClass('is-invalid');
                missing.push(label(el, fallback));
            } else $(el).removeClass('is-invalid');
        }

        if ($('#substitutoSwitch').is(':checked')) check('exDocumentoDTO.titularSel.sigla', 'Substituto do Responsavel pela Assinatura');
        if ($('#cossignatariosSwitch').is(':checked')) check('exDocumentoDTO.cosignatarioSel.sigla', 'Outros Assinantes / Cossignatarios');

        if ($('#personalizacaoSwitch').is(':checked')) {
            [['personalizarFuncao','Funcao'],['personalizarUnidade','Lotacao'],['personalizarLocalidade','Cidade'],['personalizarNome','Nome']].forEach(function(item) {
                var el = document.getElementById(item[0]);
                if (el && (!el.value || !el.value.trim())) {
                    $(el).addClass('is-invalid');
                    missing.push(item[1]);
                } else if (el) $(el).removeClass('is-invalid');
            });
        }
        return missing;
    }

    var oldGravar = window.gravarDoc;
    var oldFinalizar = window.gravarAssinarDoc;

    window.gravarDoc = function() {
        var missing = ensureConditionalRequired();
        if (missing.length) {
            show(missing, false);
            return false;
        }
        return oldGravar ? oldGravar.apply(this, arguments) : false;
    };

    window.gravarAssinarDoc = function() {
        var missing = ensureConditionalRequired();
        if (missing.length) {
            try { if (window.sigaSpinner && window.sigaSpinner.ocultar) window.sigaSpinner.ocultar(); } catch (e) {}
            show(missing, true);
            return false;
        }
        return oldFinalizar ? oldFinalizar.apply(this, arguments) : false;
    };
})(window, document, window.jQuery);
