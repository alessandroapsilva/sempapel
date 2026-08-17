from pathlib import Path

p = Path('sigaex/src/main/webapp/WEB-INF/page/exDocumento/edita.jsp')
s = p.read_text(encoding='utf-8')

old = '''\t\t\t\t\t<!-- BOTÕES -->
\t\t\t\t\t<div class="row mt-4">
\t\t\t\t\t\t<div class="col-sm-8">
\t\t\t\t\t\t\t<button id="btnGravar" type="button" onclick="javascript: gravarDoc(); return false;" name="gravar" class="btn btn-primary" accesskey="g" title="Apenas grava o documento podendo continuar a Edição"><u>G</u>ravar</button>
\t\t\t\t\t\t\t&nbsp;
\t\t\t\t\t\t\t<button id="btnFinalizarAssinar" type="button" onclick="javascript: gravarAssinarDoc(); return false;" name="finalizareGravar" class="btn btn-primary" accesskey="f" title="Finalizar documento em definitivo e em seguida realizar assinatura digital"><u>F</u>inalizar e Assinar</button>
\t\t\t\t\t\t\t&nbsp;
\t\t\t\t\t\t\t<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info" accesskey="v" title="Visualizar o documento gerado"><u>V</u>er Documento</button>
\t\t\t\t\t\t\t&nbsp;
\t\t\t\t\t\t\t<button type="button" name="ver_doc_pdf" onclick="javascript: popitup_documento(true); return false;" class="btn btn-info" accesskey="i" title="Visualizar versão para impressão (PDF)">Ver <u>I</u>mpressão</button>
\t\t\t\t\t\t\t&nbsp;
\t\t\t\t\t\t\t<button type="button" name="voltar" onclick="javascript: history.back();" class="btn btn-info" accesskey="r" title="Voltar à página anterior">Volta<u>r</u></button>
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>'''

new = '''\t\t\t\t\t<!-- BOTÕES - padrão PBdoc -->
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

if old not in s:
    raise SystemExit('Bloco atual dos botoes nao encontrado')

p.write_text(s.replace(old, new, 1), encoding='utf-8')
