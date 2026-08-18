from pathlib import Path
import re

jsp = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
js = Path('sigaex/src/main/webapp/javascript/exDocumentoEdita.js')

s = jsp.read_text(encoding='utf-8')

# 1) Garante que o navegador carregue a versão nova do JS de edição.
s = re.sub(
    r'src="\.\./\.\./\.\./javascript/exDocumentoEdita\.js(?:\?v=[^"]*)?"',
    'src="../../../javascript/exDocumentoEdita.js?v=pbdoc-adapt-20260818-3"',
    s,
    count=1,
)

# 2) Visual dos obrigatórios: somente * vermelho, sem texto "(obrigatório)".
s = s.replace('<a style="color: red">(obrigatório)</a>', '<span class="text-danger">*</span>')
s = s.replace('<span style="color: red">(obrigatório)</span>', '<span class="text-danger">*</span>')
s = s.replace('<span class="text-danger">(obrigatório)</span>', '<span class="text-danger">*</span>')

# 3) Não pinta a caixa/input de vermelho. A classe is-invalid continua internamente
#    para a validação funcionar, mas visualmente o campo mantém a borda normal.
css_marker = 'pbdoc-required-visual-20260818'
if css_marker not in s:
    pagina = '<siga:pagina titulo="Novo Documento">'
    css = '''<siga:pagina titulo="Novo Documento">\n\t<style id="pbdoc-required-visual-20260818">\n\t\t#frm .form-control.is-invalid,\n\t\t#frm .custom-select.is-invalid,\n\t\t#frm .custom-file-input.is-invalid ~ .custom-file-label {\n\t\t\tborder-color: #ced4da !important;\n\t\t\tbackground-image: none !important;\n\t\t\tbox-shadow: none !important;\n\t\t}\n\t\t#frm .form-control.is-invalid:focus,\n\t\t#frm .custom-select.is-invalid:focus {\n\t\t\tborder-color: #80bdff !important;\n\t\t\tbox-shadow: 0 0 0 .2rem rgba(0,123,255,.25) !important;\n\t\t}\n\t</style>'''
    if pagina not in s:
        raise SystemExit('Não encontrou abertura siga:pagina no edita.jsp')
    s = s.replace(pagina, css, 1)

# 4) Bump do documento.validacao.js para evitar cache antigo.
s = re.sub(
    r'documento\.validacao\.js(?:\?v=[^"\']*)?',
    'documento.validacao.js?v=pbdoc-adapt-20260818-3',
    s,
    count=1,
)

jsp.write_text(s, encoding='utf-8')

# A validação JS já foi adaptada no commit anterior e é preservada.
# Apenas garantimos que não volte a mensagem genérica "Campo obrigatório".
j = js.read_text(encoding='utf-8')
if "nomeCampo = 'Campo obrigatório'" in j:
    j = j.replace("nomeCampo = 'Campo obrigatório'", "nomeCampo = 'Campo do modelo'")
js.write_text(j, encoding='utf-8')
