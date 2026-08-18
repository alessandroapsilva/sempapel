from pathlib import Path
import re

js = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
s = js.read_text(encoding='utf-8')

inicio = s.index('function obterCampoObrigatorioPrioritarioDocumento(mensagens) {')
fim = s.index('function exibirModalCamposObrigatoriosDocumento', inicio)

nova_funcao = '''function obterCampoObrigatorioPrioritarioDocumento(mensagens) {
\tfunction vazio(nomeSigla) {
\t\tvar el = $('[name="' + nomeSigla + '"]').first();
\t\tif (el.length == 0 || !campoDeveAparecerNoResumoDocumento(el)) return false;
\t\tvar nomeId = nomeSigla.replace('Sel.sigla', 'Sel.id');
\t\tvar id = $('[name="' + nomeId + '"]').first();
\t\tvar valor = id.length ? id.val() : el.val();
\t\treturn !String(valor || '').trim();
\t}

\t/* PBdoc: Assunto é sempre o primeiro obrigatório apresentado. */
\tvar assunto = $('[name="exDocumentoDTO.descrDocumento"]').first();
\tif (assunto.length > 0 && campoDeveAparecerNoResumoDocumento(assunto)
\t\t\t&& !String(assunto.val() || '').trim()) {
\t\treturn 'Assunto';
\t}

\tvar tipoDestinatario = String($('[name="exDocumentoDTO.tipoDestinatario"]').val() || '');
\tif (tipoDestinatario === '1' && vazio('exDocumentoDTO.destinatarioSel.sigla')) return 'Destinatário - Usuário';
\tif (tipoDestinatario === '2' && vazio('exDocumentoDTO.lotacaoDestinatarioSel.sigla')) return 'Destinatário - Lotação';
\tif (tipoDestinatario === '3' && vazio('exDocumentoDTO.orgaoExternoDestinatarioSel.sigla')) return 'Destinatário - Órgão Externo';
\tif (tipoDestinatario && ['1','2','3'].indexOf(tipoDestinatario) === -1) {
\t\tvar nmDest = $('[name="exDocumentoDTO.nmDestinatario"]').first();
\t\tif (nmDest.length && !String(nmDest.val() || '').trim()) return 'Destinatário';
\t}

\tif (vazio('exDocumentoDTO.classificacaoSel.sigla')) return 'Classificação Documental';
\tif (vazio('exDocumentoDTO.subscritorSel.sigla')) return 'Responsável pela Assinatura';
\tif ($('#substitutoSwitch').is(':checked') && vazio('exDocumentoDTO.titularSel.sigla')) return 'Titular';

\tvar invalido = $('#frm').find('.is-invalid').filter(function() {
\t\treturn campoDeveAparecerNoResumoDocumento($(this));
\t}).first();
\tif (invalido.length > 0) {
\t\tvar div = obterMensagemDivErro(invalido);
\t\tvar nomeSalvo = limparNomeCampoDocumento(div.attr('data-nome-campo-documento'));
\t\tif (nomeSalvo && !/^(Campo obrigatório|um campo obrigatório)$/i.test(nomeSalvo)) return nomeSalvo;
\t\tvar nomeReal = limparNomeCampoDocumento(obterNomeCampoDocumento(invalido));
\t\tif (nomeReal && !/^(Campo obrigatório|um campo obrigatório)$/i.test(nomeReal)) return nomeReal;
\t}

\tif (mensagens && mensagens.length) {
\t\tvar m = String(mensagens[0] || '')
\t\t\t.replace(/^Favor\\s+(preencher|informar|selecionar|selecione)\\s+(o\\s+|a\\s+)?campo\\s*/i, '')
\t\t\t.replace(/^Preencha\\s+(o\\s+|a\\s+)?campo\\s*/i, '')
\t\t\t.replace(/[.'\"]+$/g, '')
\t\t\t.trim();
\t\tif (m && !/^(Campo obrigatório|um campo obrigatório)$/i.test(m)) return m;
\t}

\tvar obrigatorios = $('#frm').find('[name=obrigatorios]');
\tfor (var i = 0; i < obrigatorios.length; i++) {
\t\tvar el = $('[name="' + obrigatorios[i].value + '"]').first();
\t\tif (!el.length || !campoDeveAparecerNoResumoDocumento(el)) continue;
\t\tvar nome = limparNomeCampoDocumento(obterNomeCampoDocumento(el));
\t\tif (nome && !/^(Campo obrigatório|um campo obrigatório)$/i.test(nome)) return nome;
\t}

\treturn 'Campo do documento';
}

'''

s = s[:inicio] + nova_funcao + s[fim:]

antigo = '''\t/* Padrão PBdoc: obrigatório é informado somente no modal, sem pintar campos de vermelho. */
\t$('#frm').find('.is-invalid').each(function() {
\t\tvar campo = $(this);
\t\tremoverElementoInvalido(campo);
\t\tremoverLabelInvalido(campo);
\t\tobterMensagemDivErro(campo).text('');
\t});'''
novo = '''\t/* Sem borda vermelha: mantém apenas o texto/label do campo obrigatório em vermelho. */
\t$('#frm').find('.is-invalid').each(function() {
\t\tvar campo = $(this);
\t\tremoverElementoInvalido(campo);
\t\tobterMensagemDivErro(campo).text('');
\t});'''
if antigo not in s:
    raise SystemExit('Bloco visual esperado não encontrado')
s = s.replace(antigo, novo, 1)

js.write_text(s, encoding='utf-8')

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
t = jsp.read_text(encoding='utf-8')
antiga_versao = 'documento.validacao.js?v=pbdoc-final-20260817-3'
nova_versao = 'documento.validacao.js?v=pbdoc-nomes-reais-20260817-4'
if antiga_versao not in t:
    raise SystemExit('Versão atual do JS não encontrada no edita.jsp')
t = t.replace(antiga_versao, nova_versao, 1)
jsp.write_text(t, encoding='utf-8')
