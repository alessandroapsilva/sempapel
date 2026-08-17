from pathlib import Path
js=Path('sigaex/src/main/webapp/javascript/exDocumentoEdita.js')
s=js.read_text(encoding='utf-8')
ini=s.index("\tif (camposInvalidos.length > 0) {")
fim=s.index("\n\tif (descricaoAutomatica == null",ini)
novo="""\tif (camposInvalidos.length > 0) {
\t\tif (!silencioso) {
\t\t\tvar assunto = $('[name=\"exDocumentoDTO.descrDocumento\"]').first();
\t\t\tvar primeiro = (assunto.length > 0 && assunto.hasClass('is-invalid')) ? assunto : camposInvalidos.first();
\t\t\tvar nomeCampo = '';
\t\t\tif (typeof obterNomeCampoDocumento === 'function') nomeCampo = obterNomeCampoDocumento(primeiro);
\t\t\tif (typeof limparNomeCampoDocumento === 'function') nomeCampo = limparNomeCampoDocumento(nomeCampo);
\t\t\tif (!nomeCampo && primeiro.is(assunto)) nomeCampo = 'Assunto';
\t\t\tif (!nomeCampo) nomeCampo = 'Campo obrigatório';
\t\t\tvar acao = finalizar ? 'finalizar e assinar o documento' : 'gravar o documento';
\t\t\taviso(\"Preencha o campo '\" + nomeCampo + \"' antes de \" + acao + \".\", false, primeiro[0]);
\t\t\treturn false;
\t\t}
\t\treturn false;
\t}
"""
js.write_text(s[:ini]+novo+s[fim:],encoding='utf-8')
jsp=Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
t=jsp.read_text(encoding='utf-8')
t=t.replace('../../../javascript/exDocumentoEdita.js\"></script>','../../../javascript/exDocumentoEdita.js?v=pbdoc-final-20260817\"></script>',1)
jsp.write_text(t,encoding='utf-8')
