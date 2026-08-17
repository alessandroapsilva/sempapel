from pathlib import Path
import re

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
s = jsp.read_text(encoding='utf-8')

# Mantém os botões no padrão PBdoc e garante Ver Documento para documento interno,
# sem depender do tipo de modelo/template.
pattern = re.compile(
    r"(<c:if test='\$\{exDocumentoDTO\.tipoDocumento == \"interno\"\}'>\s*)"
    r"<c:if test=\"\$\{not empty exDocumentoDTO\.modelo\.nmArqMod or exDocumentoDTO\.modelo\.conteudoTpBlob == 'template/freemarker'\}\">\s*"
    r"(?P<buttons><button type=\"button\" name=\"ver_doc\".*?<button type=\"button\" name=\"voltar\".*?</button>)\s*"
    r"</c:if>\s*</c:if>",
    re.S,
)

m = pattern.search(s)
if not m:
    raise SystemExit('Bloco condicional dos botões Ver Documento/Impressão/Voltar não encontrado')

buttons = m.group('buttons')
replacement = m.group(1) + buttons + '\n\t\t\t\t\t\t\t</c:if>'
s = s[:m.start()] + replacement + s[m.end():]

# Força cache-bust do JS de validação.
s = re.sub(
    r'\.\./\.\./\.\./javascript/documento\.validacao\.js(?:\?v=[^\"]*)?',
    '../../../javascript/documento.validacao.js?v=pbdoc-modal-20260817-3',
    s,
    count=1,
)

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

\t\t/* PBdoc: campo obrigatório fica destacado, mas o texto aparece somente no modal. */
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

t = t.replace(old2, new2, 1)
js.write_text(t, encoding='utf-8')
