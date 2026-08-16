(function () {
    'use strict';

    function $id(id) {
        return document.getElementById(id);
    }

    function compactarSigla(sigla) {
        if (!sigla) return '';
        return String(sigla).replace(/-/g, '').replace(/\//g, '').trim();
    }

    function texto(el) {
        return el ? (el.textContent || '').trim() : '';
    }

    function normalizar(valor) {
        return String(valor || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function aplicarAjustesVisuaisPbdoc() {
        /* Mantém os botões/ações existentes do ENFAS. Apenas organiza a tela no
         * padrão estrutural do PBdoc e remove hacks antigos que não pertencem ao
         * exibe.jsp original. */
        var fallback = $id('btn-assinar-fallback');
        if (fallback) fallback.remove();

        var voltar = document.querySelector('button[name="voltar"]');
        if (voltar) voltar.remove();

        var css = document.createElement('style');
        css.id = 'enfas-exibe-pbdoc-css';
        css.textContent = [
            '#page.container-fluid.content{padding-left:20px;padding-right:20px;}',
            '.siga-menu-acoes{margin-bottom:.35rem;}',
            '.siga-menu-acoes .btn{margin-right:.2rem;margin-bottom:.2rem;}',
            '.gt-sidebar .card-sidebar{margin-bottom:.75rem!important;}',
            '.gt-sidebar .card-header{padding:.55rem .85rem;}',
            '.gt-sidebar .card-body{padding:.75rem .9rem;}',
            '.sigla-documento{margin-bottom:.35rem;}',
            '#movsTable{margin-top:.4rem;}',
            '#movsTable th,#movsTable td{vertical-align:middle;}',
            '.select2-container{width:100%!important;}',
            '.enfas-filtro-historico{margin-bottom:.75rem;}',
            '.enfas-filtro-historico label{margin-bottom:.2rem;}',
            '.container-files{position:relative;}',
            '.files .btn.btn-sm.btn-light{width:84%;text-align:left;}',
            '@media (max-width:767.98px){#page.container-fluid.content{padding-left:10px;padding-right:10px}.gt-sidebar{margin-top:1rem;}}'
        ].join('\n');
        if (!$id(css.id)) document.head.appendChild(css);
    }

    function removerDuplicados(select) {
        if (!select) return;
        var vistos = new Set();
        Array.from(select.options).forEach(function (op) {
            var chave = normalizar(op.value || op.text);
            if (vistos.has(chave)) op.remove();
            else vistos.add(chave);
        });
    }

    function ordenarSelect(select) {
        if (!select) return;
        var opcoes = Array.from(select.options);
        opcoes.sort(function (a, b) {
            return a.text.localeCompare(b.text, 'pt-BR', { sensitivity: 'base' });
        });
        opcoes.forEach(function (op) { select.appendChild(op); });
    }

    function inicializarSelect2() {
        if (!window.jQuery || !jQuery.fn || !jQuery.fn.select2) return;
        ['lotacaoSelect', 'modeloSelect', 'especieSelect'].forEach(function (id) {
            var el = $id(id);
            if (!el) return;
            var $el = jQuery(el);
            if ($el.hasClass('select2-hidden-accessible')) $el.select2('destroy');
            $el.select2({ width: '100%', closeOnSelect: false });
            $el.removeClass('default-select');
        });
    }

    function preencherSelect(select, itens, valueFn, textFn) {
        if (!select || !Array.isArray(itens)) return;
        var valores = new Set(Array.from(select.options).map(function (op) {
            return normalizar(op.value + '|' + op.text);
        }));
        itens.forEach(function (item) {
            var value = valueFn(item);
            var label = textFn(item);
            if (!label) return;
            var chave = normalizar(value + '|' + label);
            if (valores.has(chave)) return;
            valores.add(chave);
            var op = document.createElement('option');
            op.value = value == null ? label : value;
            op.text = label;
            select.appendChild(op);
        });
        ordenarSelect(select);
        removerDuplicados(select);
    }

    function carregarEspecies() {
        var select = $id('especieSelect');
        if (!select || !window.jQuery) return;
        jQuery.ajax({
            url: '/sigaex/api/v1/especies',
            dataType: 'json',
            timeout: 15000,
            success: function (result) {
                var especies = result && Array.isArray(result.especies) ? result.especies : [];
                preencherSelect(select, especies,
                    function (e) { return Array.isArray(e) ? e[0] : (e.id || e.idEspecie); },
                    function (e) { return Array.isArray(e) ? e[1] : (e.nome || e.descricao); });
                inicializarSelect2();
            }
        });
    }

    function carregarModelos() {
        var select = $id('modeloSelect');
        if (!select || !window.jQuery) return;
        jQuery.ajax({
            url: '/sigaex/api/v1/modelos/lista-hierarquica',
            dataType: 'json',
            timeout: 15000,
            success: function (result) {
                var modelos = result && Array.isArray(result.list) ? result.list : [];
                preencherSelect(select, modelos,
                    function (m) { return m.idModelo || m.id; },
                    function (m) { return m.nome || m.descricao; });
                inicializarSelect2();
            }
        });
    }

    function selecionados(id) {
        var select = $id(id);
        if (!select) return [];
        return Array.from(select.selectedOptions || []).map(function (op) {
            return normalizar(op.text || op.value);
        });
    }

    function getDocumentoDaMovimentacao(row) {
        if (!row || !row.cells || row.cells.length < 4) return '';
        var link = row.cells[3].querySelector('a');
        return texto(link);
    }

    var cacheDocumento = Object.create(null);

    function consultarDetalhes(sigla) {
        sigla = compactarSigla(sigla);
        if (!sigla) return null;
        if (Object.prototype.hasOwnProperty.call(cacheDocumento, sigla)) return cacheDocumento[sigla];
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/sigaex/api/v1/documentos/' + encodeURIComponent(sigla) + '/detalhes', false);
            xhr.send();
            if (xhr.status >= 200 && xhr.status < 300) {
                cacheDocumento[sigla] = JSON.parse(xhr.responseText || '{}');
                return cacheDocumento[sigla];
            }
        } catch (e) {
            console.warn('Não foi possível consultar detalhes do documento', sigla, e);
        }
        cacheDocumento[sigla] = null;
        return null;
    }

    function modeloDoDocumento(sigla) {
        var d = consultarDetalhes(sigla);
        return normalizar(d && (d.nomeDoModelo || d.modelo || d.modeloNome));
    }

    function especieDoDocumento(sigla) {
        var d = consultarDetalhes(sigla);
        return normalizar(d && (d.especie || d.especieNome || d.forma));
    }

    function aplicarFiltro() {
        var lotacoes = selecionados('lotacaoSelect');
        var modelos = selecionados('modeloSelect');
        var especies = selecionados('especieSelect');
        var rows = document.querySelectorAll('#movsTable tbody tr');

        rows.forEach(function (row) {
            var lotacao = row.cells && row.cells[1] ? normalizar(texto(row.cells[1])) : '';
            var documento = getDocumentoDaMovimentacao(row);
            var okLotacao = !lotacoes.length || lotacoes.indexOf(lotacao) >= 0;
            var okModelo = true;
            var okEspecie = true;

            if (modelos.length && documento) okModelo = modelos.indexOf(modeloDoDocumento(documento)) >= 0;
            if (especies.length && documento) okEspecie = especies.indexOf(especieDoDocumento(documento)) >= 0;

            row.classList.toggle('hidden-row', !(okLotacao && okModelo && okEspecie));
        });

        var verTodos = $id('showAllButton');
        if (verTodos) verTodos.style.display = 'inline-block';
    }

    function mostrarTodos() {
        document.querySelectorAll('#movsTable tbody tr').forEach(function (row) {
            row.classList.remove('hidden-row');
        });
        var verTodos = $id('showAllButton');
        if (verTodos) verTodos.style.display = 'none';
    }

    function prepararFiltros() {
        var lotacao = $id('lotacaoSelect');
        if (lotacao) {
            ordenarSelect(lotacao);
            removerDuplicados(lotacao);
        }
        var filtrar = $id('filterButton');
        var todos = $id('showAllButton');
        if (filtrar) filtrar.onclick = aplicarFiltro;
        if (todos) {
            todos.onclick = mostrarTodos;
            todos.style.display = 'none';
        }
        inicializarSelect2();
        carregarModelos();
        carregarEspecies();
    }

    function init() {
        aplicarAjustesVisuaisPbdoc();
        prepararFiltros();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    /* Mantém compatibilidade com chamadas inline já existentes no exibe.jsp. */
    window.applyFilter = aplicarFiltro;
    window.showAll = mostrarTodos;
    window.showAllRows = mostrarTodos;
    window.compactarSigla = compactarSigla;
})();
