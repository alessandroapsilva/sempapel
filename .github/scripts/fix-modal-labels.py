from pathlib import Path
import re

p = Path('sigaex/src/main/webapp/javascript/documento.validacao.js')
s = p.read_text(encoding='utf-8')

pattern = r"function obterCampoObrigatorioPrioritarioDocumento\(mensagens\) \{.*?\n\}\n\nfunction exibirModalCamposObrigatoriosDocumento"
replacement = '''function obterCampoObrigatorioPrioritarioDocumento(mensagens) {
\tvar assunto = $('[name="exDocumentoDTO.descrDocumento"]').first();
\tif (assunto.length > 0 && campoDeveAparecerNoResumoDocumento(assunto)
\t\t\t&& !String(assunto.val() || '').trim()) {
\t\treturn limparNomeCampoDocumento(obterNomeCampoDocumento(assunto)) || 'Assunto';
\t}

\tvar invalido = $('#frm').find('.is-invalid').filter(function() {
\t\treturn campoDeveAparecerNoResumoDocumento($(this));
\t}).first();

\tif (invalido.length > 0) {
\t\tvar nomeReal = limparNomeCampoDocumento(obterNomeCampoDocumento(invalido));
\t\tif (nomeReal) return nomeReal;
\t}

\tif (mensagens && mensagens.length) {
\t\tvar m = String(mensagens[0] || '')
\t\t\t.replace(/^Favor\\s+(preencher|informar|selecionar)\\s+(o\\s+|a\\s+)?campo\\s*/i, '')
\t\t\t.replace(/^Preencha\\s+(o\\s+|a\\s+)?campo\\s*/i, '')
\t\t\t.replace(/[.'\\"]+$/g, '')
\t\t\t.trim();
\t\tif (m) return m;
\t}
\n\treturn 'Campo obrigatório';
}

function exibirModalCamposObrigatoriosDocumento'''

s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('funcao prioritária nao encontrada')
s = s2

s = s.replace("validarSelecaoObrigatoriaDocumento('exDocumentoDTO.subscritorSel.sigla', 'Responsável pela Assinatura');", "validarSelecaoObrigatoriaDocumento('exDocumentoDTO.subscritorSel.sigla');")
s = s.replace("validarSelecaoObrigatoriaDocumento('exDocumentoDTO.titularSel.sigla', 'Substituto Responsável pela Assinatura');", "validarSelecaoObrigatoriaDocumento('exDocumentoDTO.titularSel.sigla');")
s = s.replace("validarSelecaoObrigatoriaDocumento('exDocumentoDTO.classificacaoSel.sigla', 'Tipo Documental');", "validarSelecaoObrigatoriaDocumento('exDocumentoDTO.classificacaoSel.sigla');")
s = s.replace("validarCampoObrigatorioDocumento('exDocumentoDTO.descrDocumento', 'Assunto');", "validarCampoObrigatorioDocumento('exDocumentoDTO.descrDocumento');")

p.write_text(s, encoding='utf-8')
