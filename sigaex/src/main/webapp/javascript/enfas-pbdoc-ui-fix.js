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

    var FIELD_NAMES = {
        'exDocumentoDTO.subscritorSel.sigla': 'Responsável pela Assinatura',
        'exDocumentoDTO.subscritorSel.id': 'Responsável pela Assinatura',
        'exDocumentoDTO.titularSel.sigla': 'Titular',
        'exDocumentoDTO.titularSel.id': 'Titular',
        'exDocumentoDTO.destinatarioSel.sigla': 'Destinatário',
        'exDocumentoDTO.destinatarioSel.id': 'Destinatário',
        'exDocumentoDTO.lotacaoDestinatarioSel.sigla': 'Destinatário',
        'exDocumentoDTO.lotacaoDestinatarioSel.id': 'Destinatário',
        'exDocumentoDTO.orgaoExternoDestinatarioSel.sigla': 'Destinatário',
        'exDocumentoDTO.orgaoExternoDestinatarioSel.id': 'Destinatário',
        'exDocumentoDTO.nmDestinatario': 'Destinatário',
        'exDocumentoDTO.classificacaoSel.sigla': 'Tipo Documental',
        'exDocumentoDTO.classificacaoSel.id': 'Tipo Documental',
        'exDocumentoDTO.descrDocumento': 'Assunto',
        'exDocumentoDTO.dtDocString': 'Data',
        'exDocumentoDTO.idMod': 'Modelo',
        'exDocumentoDTO.cosignatarioSel.sigla': 'Cossignatários',
        'exDocumentoDTO.cosignatarioSel.id': 'Cossignatários',
        'personalizarFuncao': 'Função',
        'personalizarUnidade': 'Lotação',
        'personalizarLocalidade': 'Cidade',
        'personalizarNome': 'Nome'
    };

    function friendlyName(el) {
        if (!el) return '';

        var key = el.name || el.id || '';
        if (FIELD_NAMES[key]) return FIELD_NAMES[key];

        var group = $(el).closest('.form-group');
        if (group.length) {
            var labels = group.find('label').filter(function() {
                return clean($(this).text()).length > 0;
            });
            if (labels.length) {
                var labelText = clean(labels.first().clone().find('a,span,i,small').remove().end().text());
                if (labelText && labelText !== 'Campo obrigatório') return labelText;
            }
        }

        var row = $(el).closest('.row');
        if (row.length) {
            var rowLabels = row.find('label').filter(function() {
                var t = clean($(this).text());
                return t && t !== 'Campo obrigatório' && t !== ' ';
            });
            if (rowLabels.length) {
                var rowText = clean(rowLabels.first().clone().find('a,span,i,small').remove().end().text());
                if (rowText) return rowText;
            }
        }

        var title = clean(el.getAttribute('title'));
        if (title && title.toLowerCase() !== 'campo obrigatório') return title;

        var placeholder = clean(el.getAttribute('placeholder'));
        if (placeholder) return placeholder;

        if (/subscritor/i.test(key)) return 'Responsável pela Assinatura';
        if (/titular/i.test(key)) return 'Titular';
        if (/destinat/i.test(key)) return 'Destinatário';
        if (/classificacao/i.test(key)) return 'Tipo Documental';
        if (/descrDocumento/i.test(key)) return 'Assunto';
        if (/funcao/i.test(key)) return 'Função';
        if (/unidade|lotacao/i.test(key)) return 'Lotação';
        if (/localidade|cidade/i.test(key)) return 'Cidade';
        if (/nome/i.test(key)) return 'Nome';
        if (/modelo|idMod/i.test(key)) return 'Modelo';

        return '';
    }

    function findInvalidFieldName() {
        var invalid = $('#frm .is-invalid:visible').filter(function() {
            return this.type !== 'hidden' && !$(this).is(':disabled');
        });

        for (var i = 0; i < invalid.length; i++) {
            var name = friendlyName(invalid[i]);
            if (name) return name;
        }

        var required = $('#frm [required]:visible, #frm [aria-required="true"]:visible').filter(function() {
            if ($(this).is(':disabled') || this.type === 'hidden') return false;
            if (this.type === 'checkbox' || this.type === 'radio') {
                return !$('[name="' + this.name + '"]:checked').length;
            }
            return !String($(this).val() || '').trim();
        });

        for (var j = 0; j < required.length; j++) {
            var requiredName = friendlyName(required[j]);
            if (requiredName) return requiredName;
        }

        return '';
    }

    function patchModal() {
        if (!window.sigaModal || typeof window.sigaModal.alerta !== 'function') return;
        if (window.sigaModal.alerta._enfasPbdocPatched) return;

        var original = window.sigaModal.alerta;
        var patched = function(message) {
            var msg = String(message || '');
            if (/Campo obrigat[oó]rio/i.test(msg)) {
                var nome = findInvalidFieldName();
                if (nome) {
                    msg = "Preencha o campo '" + nome + "' antes de gravar o documento.";
                }
            }
            return original.call(window.sigaModal, msg);
        };
        patched._enfasPbdocPatched = true;
        window.sigaModal.alerta = patched;
    }

    function styleButtonsLikePBdoc() {
        if (window.location.pathname.indexOf('/app/expediente/doc/editar') < 0) return;

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
            parent.style.gap = '4px';

            Array.prototype.slice.call(parent.childNodes).forEach(function(node) {
                if (node.nodeType === 3 && !String(node.nodeValue || '').replace(/\u00a0/g, '').trim()) {
                    node.nodeValue = '';
                }
            });
        }

        buttons.forEach(function(btn) {
            btn.style.margin = '0';
        });

        var gravar = buttons[0];
        if (gravar) {
            gravar.className = 'btn btn-primary';
            gravar.innerHTML = '<u>G</u>ravar';
        }

        var finalizar = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
        if (finalizar) {
            finalizar.className = 'btn btn-primary';
            finalizar.innerHTML = '<u>F</u>inalizar e Assinar';
        }

        var verDoc = document.querySelector('button[name="ver_doc"]');
        if (verDoc) {
            verDoc.className = 'btn btn-info';
            verDoc.innerHTML = '<u>V</u>er Documento';
        }

        var verPdf = document.querySelector('button[name="ver_doc_pdf"]');
        if (verPdf) {
            verPdf.className = 'btn btn-info';
            verPdf.innerHTML = 'Ver <u>I</u>mpressão';
        }

        var voltar = document.querySelector('button[name="voltar"]');
        if (voltar) {
            voltar.className = 'btn btn-info';
            voltar.innerHTML = 'Volta<u>r</u>';
        }
    }

    function annotateFields() {
        $('#frm input, #frm select, #frm textarea').each(function() {
            var name = friendlyName(this);
            if (name && (!this.title || /Campo obrigat[oó]rio/i.test(this.title))) {
                this.title = name;
            }
        });
    }

    function install() {
        if (window.location.pathname.indexOf('/app/expediente/doc/editar') < 0) return;
        annotateFields();
        patchModal();
        styleButtonsLikePBdoc();

        setTimeout(function() {
            annotateFields();
            patchModal();
            styleButtonsLikePBdoc();
        }, 250);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install);
    } else {
        install();
    }
})(window, document, window.jQuery);
