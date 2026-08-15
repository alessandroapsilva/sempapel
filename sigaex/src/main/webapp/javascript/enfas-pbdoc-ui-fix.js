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
        'exDocumentoDTO.destinatarioSel.sigla': 'Destinatário - Usuário',
        'exDocumentoDTO.destinatarioSel.id': 'Destinatário - Usuário',
        'exDocumentoDTO.lotacaoDestinatarioSel.sigla': 'Destinatário - Lotação',
        'exDocumentoDTO.lotacaoDestinatarioSel.id': 'Destinatário - Lotação',
        'exDocumentoDTO.orgaoExternoDestinatarioSel.sigla': 'Destinatário - Órgão Externo',
        'exDocumentoDTO.orgaoExternoDestinatarioSel.id': 'Destinatário - Órgão Externo',
        'exDocumentoDTO.nmDestinatario': 'Destinatário - Campo Livre',
        'exDocumentoDTO.classificacaoSel.sigla': 'Tipo Documental',
        'exDocumentoDTO.classificacaoSel.id': 'Tipo Documental',
        'exDocumentoDTO.descrDocumento': 'Assunto',
        'descrDocumento': 'Assunto',
        'exDocumentoDTO.dtDocString': 'Data',
        'exDocumentoDTO.idMod': 'Modelo',
        'exDocumentoDTO.cosignatarioSel.sigla': 'Cossignatários',
        'exDocumentoDTO.cosignatarioSel.id': 'Cossignatários',
        'personalizarFuncao': 'Função',
        'personalizarUnidade': 'Lotação',
        'personalizarLocalidade': 'Cidade',
        'personalizarNome': 'Nome'
    };

    function byName(name) {
        var els = document.getElementsByName(name);
        return els && els.length ? els[0] : null;
    }

    function isVisible(el) {
        if (!el || $(el).is(':disabled')) return false;
        if ($(el).closest('.d-none,[hidden]').length) return false;
        var styleParent = $(el).closest('[style]');
        if (styleParent.length && /display\s*:\s*none/i.test(styleParent.attr('style') || '')) return false;
        return $(el).is(':visible');
    }

    function hasValue(el) {
        return !!(el && String($(el).val() || '').trim());
    }

    function selectionHasValue(siglaName) {
        var sigla = byName(siglaName);
        var id = byName(siglaName.replace('Sel.sigla', 'Sel.id'));
        return hasValue(id) || hasValue(sigla);
    }

    function destinatarioSelecionado() {
        var tipo = byName('exDocumentoDTO.tipoDestinatario');
        if (!tipo || !isVisible(tipo)) return null;

        var valor = String(tipo.value || '');
        if (valor === '1') return { nome: 'Destinatário - Usuário', vazio: !selectionHasValue('exDocumentoDTO.destinatarioSel.sigla') };
        if (valor === '2') return { nome: 'Destinatário - Lotação', vazio: !selectionHasValue('exDocumentoDTO.lotacaoDestinatarioSel.sigla') };
        if (valor === '3') return { nome: 'Destinatário - Órgão Externo', vazio: !selectionHasValue('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla') };
        return { nome: 'Destinatário - Campo Livre', vazio: !hasValue(byName('exDocumentoDTO.nmDestinatario')) };
    }

    function friendlyName(el) {
        if (!el) return '';
        var key = el.name || el.id || '';
        if (FIELD_NAMES[key]) return FIELD_NAMES[key];

        var group = $(el).closest('.form-group');
        if (group.length) {
            var labels = group.find('label').filter(function() { return clean($(this).text()).length > 0; });
            if (labels.length) {
                var labelText = clean(labels.first().clone().find('a,span,i,small').remove().end().text());
                if (labelText && !/Campo obrigat[oó]rio/i.test(labelText)) return labelText;
            }
        }

        var title = clean(el.getAttribute('title'));
        if (title && !/Campo obrigat[oó]rio/i.test(title)) return title;

        if (/subscritor/i.test(key)) return 'Responsável pela Assinatura';
        if (/titular/i.test(key)) return 'Titular';
        if (/lotacaoDestinatario/i.test(key)) return 'Destinatário - Lotação';
        if (/orgaoExternoDestinatario/i.test(key)) return 'Destinatário - Órgão Externo';
        if (/destinatario/i.test(key)) return 'Destinatário - Usuário';
        if (/classificacao/i.test(key)) return 'Tipo Documental';
        if (/descrDocumento/i.test(key)) return 'Assunto';
        if (/funcao/i.test(key)) return 'Função';
        if (/unidade|lotacao/i.test(key)) return 'Lotação';
        if (/localidade|cidade/i.test(key)) return 'Cidade';
        if (/nome/i.test(key)) return 'Nome';
        if (/modelo|idMod/i.test(key)) return 'Modelo';
        return '';
    }

    function firstRequiredFieldName() {
        var assunto = byName('exDocumentoDTO.descrDocumento') || document.getElementById('descrDocumento');
        if (assunto && isVisible(assunto) && !hasValue(assunto)) {
            $(assunto).addClass('is-invalid');
            return 'Assunto';
        }

        var destinatario = destinatarioSelecionado();
        if (destinatario && destinatario.vazio) return destinatario.nome;

        if (!selectionHasValue('exDocumentoDTO.subscritorSel.sigla')) return 'Responsável pela Assinatura';

        var substituto = byName('exDocumentoDTO.substituicao');
        if (substituto && substituto.checked && !selectionHasValue('exDocumentoDTO.titularSel.sigla')) return 'Substituto Responsável pela Assinatura';

        var invalid = $('#frm .is-invalid:visible').filter(function() {
            return this.type !== 'hidden' && !$(this).is(':disabled');
        });
        for (var i = 0; i < invalid.length; i++) {
            var name = friendlyName(invalid[i]);
            if (name && !/Campo obrigat[oó]rio/i.test(name)) return name;
        }

        var required = $('#frm [required]:visible, #frm [aria-required="true"]:visible').filter(function() {
            if ($(this).is(':disabled') || this.type === 'hidden') return false;
            if (this.type === 'checkbox' || this.type === 'radio') return !$('[name="' + this.name + '"]:checked').length;
            return !String($(this).val() || '').trim();
        });
        for (var j = 0; j < required.length; j++) {
            var requiredName = friendlyName(required[j]);
            if (requiredName && !/Campo obrigat[oó]rio/i.test(requiredName)) return requiredName;
        }
        return '';
    }

    function patchModal() {
        if (!window.sigaModal || typeof window.sigaModal.alerta !== 'function') return;
        if (window.sigaModal.alerta._enfasPbdocTextoCompleto) return;

        var original = window.sigaModal.alerta;
        var patched = function(message) {
            var msg = String(message || '');
            var nome = firstRequiredFieldName();
            var ehValidacao = /Campo obrigat[oó]rio/i.test(msg) || /Favor\s+(preencher|informar|selecionar|verificar)/i.test(msg) || /Preencha\s+(o\s+|a\s+)?campo/i.test(msg) || /antes de gravar o documento/i.test(msg);
            if (ehValidacao && nome) {
                msg = "Preencha o campo '" + nome + "' antes de gravar o documento.";
            }
            return original.call(window.sigaModal, msg);
        };
        patched._enfasPbdocPatched = true;
        patched._enfasPbdocPatchedV2 = true;
        patched._enfasPbdocPatchedV3 = true;
        patched._enfasPbdocTextoCompleto = true;
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
            parent.style.columnGap = '2px';
            parent.style.rowGap = '2px';
        }
        buttons.forEach(function(btn) { btn.style.margin = '0'; btn.style.marginRight = '0'; btn.style.marginLeft = '0'; });

        var gravar = document.getElementById('btnGravar');
        if (gravar) { gravar.className = 'btn btn-primary'; gravar.innerHTML = '<u>G</u>ravar'; }
        var finalizar = document.getElementById('btnFinalizarAssinar') || document.querySelector('button[name="finalizareGravar"]');
        if (finalizar) { finalizar.className = 'btn btn-primary'; finalizar.innerHTML = '<u>F</u>inalizar e Assinar'; }
        var verDoc = document.querySelector('button[name="ver_doc"]');
        if (verDoc) { verDoc.className = 'btn btn-info'; verDoc.innerHTML = '<u>V</u>er Documento'; }
        var verPdf = document.querySelector('button[name="ver_doc_pdf"]');
        if (verPdf) { verPdf.className = 'btn btn-info'; verPdf.innerHTML = 'Ver <u>I</u>mpressão'; }
        var voltar = document.querySelector('button[name="voltar"]');
        if (voltar) { voltar.className = 'btn btn-info'; voltar.innerHTML = 'Volta<u>r</u>'; }
    }

    function annotateFields() {
        $('#frm input, #frm select, #frm textarea').each(function() {
            var name = friendlyName(this);
            if (name && (!this.title || /Campo obrigat[oó]rio/i.test(this.title))) this.title = name;
        });
    }

    function trocarMatriculaPorUsuario(root) {
        var $root = root ? $(root) : $(document);
        $root.find('th,td,label,span,div,a').addBack('th,td,label,span,div,a').each(function() {
            if (this.children && this.children.length) return;
            var txt = clean(this.textContent);
            if (txt === 'Matrícula' || txt === 'Matricula') this.textContent = 'Usuário';
        });
    }

    function installRecipientObserver() {
        trocarMatriculaPorUsuario(document);
        if (!window.MutationObserver || !document.body) return;
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                for (var i = 0; i < m.addedNodes.length; i++) {
                    var node = m.addedNodes[i];
                    if (node.nodeType === 1) trocarMatriculaPorUsuario(node);
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function install() {
        if (window.location.pathname.indexOf('/app/expediente/doc/editar') < 0) return;
        annotateFields();
        patchModal();
        styleButtonsLikePBdoc();
        installRecipientObserver();
        setTimeout(function() {
            annotateFields();
            patchModal();
            styleButtonsLikePBdoc();
            trocarMatriculaPorUsuario(document);
        }, 250);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
    else install();
})(window, document, window.jQuery);
