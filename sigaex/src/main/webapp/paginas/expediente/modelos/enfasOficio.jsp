<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" buffer="64kb"%>
<%@ taglib uri="http://localhost/modelostag" prefix="mod"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<mod:modelo>
  <mod:entrevista>
    <mod:grupo titulo="Conteúdo do ofício">
      <mod:grupo><mod:editor titulo="" var="textoOficio" /></mod:grupo>
    </mod:grupo>
    <mod:grupo>
      <mod:selecao titulo="Fecho" var="fecho" opcoes="Atenciosamente;Respeitosamente;Cordialmente" />
    </mod:grupo>
  </mod:entrevista>
  <mod:documento>
    <html xmlns="http://www.w3.org/1999/xhtml"><head><style type="text/css">
      @page { margin: 2cm 2cm 2cm 3cm; }
      body { font-family: Arial; font-size: 11pt; line-height: 1.5; }
      .titulo { text-align:center; font-weight:bold; margin-bottom:1.5em; }
      .assunto { margin:1em 0; }
      .corpo { text-align:justify; }
    </style></head><body>
      <p class="titulo">OFÍCIO Nº ${doc.codigo}</p>
      <p style="text-align:right">${doc.dtExtenso}</p>
      <c:if test="${not empty doc.destinatarioString}"><p><strong>À/Ao:</strong> <c:out value="${doc.destinatarioString}" /></p></c:if>
      <c:if test="${not empty doc.descrDocumento}"><p class="assunto"><strong>Assunto:</strong> <c:out value="${doc.descrDocumento}" /></p></c:if>
      <div class="corpo">${textoOficio}</div>
      <p>${empty fecho ? 'Atenciosamente' : fecho},</p>
      <c:import url="/paginas/expediente/modelos/inc_assinatura.jsp?formatarOrgao=sim" />
    </body></html>
  </mod:documento>
</mod:modelo>
