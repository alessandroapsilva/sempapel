from pathlib import Path

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
s = jsp.read_text(encoding='utf-8')

old = '''\t\t\t\t\t<!-- BOTÕES -->
\t\t\t\t\t<div class="row mt-4">
\t\t\t\t\t\t<div class="col-sm-8">
\t\t\t\t\t\t\t<button id="btnGravar" type="button" onclick="javascript: gravarDoc(); return false;" name="gravar" class="btn btn-primary" accesskey="g" title="Apenas grava o documento podendo continuar a Edição"><u>G</u>ravar</button>
\t\t\t\t\t\t\t<button id="btnFinalizarAssinar" type="button" onclick="javascript: gravarAssinarDoc(); return false;" name="finalizareGravar" class="btn btn-primary" accesskey="f" title="Finalizar documento em definitivo e em seguida realizar assinatura digital"><u>F</u>inalizar e Assinar</button>
\t\t\t\t\t\t\t<c:if test='${exDocumentoDTO.tipoDocumento == "interno"}'>
\t\t\t\t\t\t\t\t<c:if test="${not empty exDocumentoDTO.modelo.nmArqMod or exDocumentoDTO.modelo.conteudoTpBlob == 'template/freemarker'}">
\t\t\t\t\t\t\t\t\t<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info ${hide_only_GOVSP}" accesskey="v"><u>V</u>er Documento</button>
\t\t\t\t\t\t\t\t\t<button type="button" name="ver_doc_pdf" onclick="javascript: popitup_documento(true); return false;" class="btn btn-info" accesskey="i"><fmt:message key="documento.btn.ver.impressao2"/></button>
\t\t\t\t\t\t\t\t\t<button type="button" name="voltar" onclick="javascript: history.back();" class="btn btn-info" accesskey="r">Volta<u>r</u></button>
\t\t\t\t\t\t\t\t</c:if>
\t\t\t\t\t\t\t</c:if>
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>'''

new = '''\t\t\t\t\t<!-- BOTÕES - padrão PBdoc -->
\t\t\t\t\t<div class="row mt-4">
\t\t\t\t\t\t<div class="col-sm-8">
\t\t\t\t\t\t\t<button id="btnGravar" type="button" onclick="javascript: gravarDoc(); return false;" name="gravar" class="btn btn-primary" accesskey="g" title="Apenas grava o documento podendo continuar a Edição"><u>G</u>ravar</button>
\t\t\t\t\t\t\t<button id="btnFinalizarAssinar" type="button" onclick="javascript: gravarAssinarDoc(); return false;" name="finalizareGravar" class="btn btn-primary" accesskey="f" title="Finalizar documento em definitivo e em seguida realizar assinatura digital"><u>F</u>inalizar e Assinar</button>
\t\t\t\t\t\t\t<c:if test='${exDocumentoDTO.tipoDocumento == "interno"}'>
\t\t\t\t\t\t\t\t<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info ${hide_only_GOVSP}" accesskey="v" title="Visualizar o documento gerado"><u>V</u>er Documento</button>
\t\t\t\t\t\t\t\t<button type="button" name="ver_doc_pdf" onclick="javascript: popitup_documento(true); return false;" class="btn btn-info" accesskey="i" title="Visualizar versão para impressão (PDF)"><fmt:message key="documento.btn.ver.impressao2"/></button>
\t\t\t\t\t\t\t\t<button type="button" name="voltar" onclick="javascript: history.back();" class="btn btn-info" accesskey="r" title="Voltar à página anterior">Volta<u>r</u></button>
\t\t\t\t\t\t\t</c:if>
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>'''

if old not in s:
    raise SystemExit('Bloco atual de botões não encontrado')
s = s.replace(old, new, 1)
s = s.replace('../../../javascript/documento.validacao.js?v=1664993973', '../../../javascript/documento.validacao.js?v=pbdoc-modal-20260817-2', 1)
jsp.write_text(s, encoding='utf-8')

js = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
t = js.read_text(encoding='utf-8')
old2 = '''\tif (mensagemDiv.length > 0) {
\t\tmensagemDiv.attr('data-nome-campo-documento', obterNomeCampoDocumento(elemento));
\t\tif (elemento[0].type === 'radio' || elemento[0].type === 'checkbox') {
\t\t\tmensagemDiv.text('');
\t\t\tmensagemDiv.last().text(mensagem);
\t\t} else {
\t\t\tmensagemDiv.text(mensagem);
\t\t}\t\t\t\t
\t}
}'''
new2 = '''\tif (mensagemDiv.length > 0) {
\t\tmensagemDiv.attr('data-nome-campo-documento', obterNomeCampoDocumento(elemento));

\t\t/* PBdoc: obrigatórios ficam destacados, mas a mensagem aparece somente no modal. */
\t\tvar somenteModal = /^Favor\\s+(preencher|selecionar|selecione|informar)\\b/i.test(String(mensagem || ''));
\t\tif (somenteModal) {
\t\t\tmensagemDiv.text('');
\t\t} else if (elemento[0].type === 'radio' || elemento[0].type === 'checkbox') {
\t\t\tmensagemDiv.text('');
\t\t\tmensagemDiv.last().text(mensagem);
\t\t} else {
\t\t\tmensagemDiv.text(mensagem);
\t\t}\t\t\t\t
\t}
}'''
if old2 not in t:
    raise SystemExit('Bloco aplicarMensagemErro não encontrado')
js.write_text(t.replace(old2, new2, 1), encoding='utf-8')
