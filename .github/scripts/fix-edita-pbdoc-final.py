from pathlib import Path
import re

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
s = jsp.read_text(encoding='utf-8')

# Ver Documento deve aparecer para documento interno, sem classe que o oculte.
s, n1 = re.subn(
    r'<button\s+type="button"\s+name="ver_doc"[^>]*onclick="javascript:\s*popitup_documento\(false\);\s*return false;"[^>]*>.*?</button>',
    '<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info" accesskey="v" title="Visualizar o documento gerado"><u>V</u>er Documento</button>',
    s,
    count=1,
    flags=re.S
)
if n1 != 1:
    raise SystemExit('Botão Ver Documento não encontrado')

# Cache-buster para garantir JS novo no navegador.
s = re.sub(r'\.\./\.\./\.\./javascript/documento\.validacao\.js\?v=[^"\']+',
           '../../../javascript/documento.validacao.js?v=pbdoc-final-20260817-3', s, count=1)

jsp.write_text(s, encoding='utf-8')

js = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
t = js.read_text(encoding='utf-8')

old = '''function exibirModalCamposObrigatoriosDocumento(mensagens, finalizar) {
\tvar elemento = obterPrimeiroCampoInvalidoDocumento();
\tvar nomeCampo = obterCampoObrigatorioPrioritarioDocumento(mensagens);
\tvar msg = "Preencha o campo '" + nomeCampo + "' antes de gravar o documento.";

\tif (typeof sigaModal !== 'undefined' && typeof sigaModal.alerta === 'function') {
\t\tvar modal = sigaModal.alerta(msg);
\t\tif (modal && typeof modal.focus === 'function') modal.focus(elemento);
\t} else {
\t\talert(msg);
\t\tif (elemento && typeof elemento.focus === 'function') elemento.focus();
\t}
}'''

new = '''function exibirModalCamposObrigatoriosDocumento(mensagens, finalizar) {
\tvar elemento = obterPrimeiroCampoInvalidoDocumento();
\tvar nomeCampo = obterCampoObrigatorioPrioritarioDocumento(mensagens);
\tvar msg = "Preencha o campo '" + nomeCampo + "' antes de gravar o documento.";

\t/* Padrão PBdoc: obrigatório é informado somente no modal, sem pintar campos de vermelho. */
\t$('#frm').find('.is-invalid').each(function() {
\t\tvar campo = $(this);
\t\tremoverElementoInvalido(campo);
\t\tremoverLabelInvalido(campo);
\t\tobterMensagemDivErro(campo).text('');
\t});

\tif (typeof sigaModal !== 'undefined' && typeof sigaModal.alerta === 'function') {
\t\tvar modal = sigaModal.alerta(msg);
\t\tif (modal && typeof modal.focus === 'function') modal.focus(elemento);
\t} else {
\t\talert(msg);
\t\tif (elemento && typeof elemento.focus === 'function') elemento.focus();
\t}
}'''

if old not in t:
    raise SystemExit('Função modal não encontrada')
t = t.replace(old, new, 1)
js.write_text(t, encoding='utf-8')
