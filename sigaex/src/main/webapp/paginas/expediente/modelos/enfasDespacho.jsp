<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" buffer="64kb"%>
<%@ taglib uri="http://localhost/modelostag" prefix="mod"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<mod:modelo>
  <mod:entrevista>
    <mod:grupo titulo="Conteúdo do despacho"><mod:grupo><mod:editor titulo="" var="textoDespacho" /></mod:grupo></mod:grupo>
  </mod:entrevista>
  <mod:documento>
    <html xmlns="http://www.w3.org/1999/xhtml"><head><style type="text/css">
      @page { margin: 2cm 2cm 2cm 3cm; }
      body { font-family: Arial; font-size: 11pt; line-height: 1.5; }
      .titulo { text-align:center; font-weight:bold; margin-bottom:1.5em; }
      .corpo { text-align:justify; }
    </style></head><body>
      <p class="titulo">DESPACHO Nº ${doc.codigo}</p>
      <c:if test="${not empty doc.descrDocumento}"><p><strong>Assunto:</strong> <c:out value="${doc.descrDocumento}" /></p></c:if>
      <c:if test="${not empty doc.destinatarioString}"><p><strong>Destino:</strong> <c:out value="${doc.destinatarioString}" /></p></c:if>
      <div class="corpo">${textoDespacho}</div>
      <p style="text-align:center">${doc.dtExtenso}</p>
      <c:import url="/paginas/expediente/modelos/inc_assinatura.jsp" />
    </body></html>
  </mod:documento>
</mod:modelo>
