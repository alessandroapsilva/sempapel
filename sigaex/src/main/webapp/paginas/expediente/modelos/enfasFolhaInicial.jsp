<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" buffer="64kb"%>
<%@ taglib uri="http://localhost/modelostag" prefix="mod"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<mod:modelo>
  <mod:entrevista>
    <mod:grupo titulo="Observações da folha inicial"><mod:grupo><mod:editor titulo="" var="observacoesFolha" /></mod:grupo></mod:grupo>
  </mod:entrevista>
  <mod:documento>
    <html xmlns="http://www.w3.org/1999/xhtml"><head><style type="text/css">
      @page { margin: 2cm 2cm 2cm 2cm; }
      body { font-family: Arial; font-size: 11pt; line-height: 1.5; }
      .titulo { text-align:center; font-weight:bold; font-size:14pt; margin:2em 0; }
      .quadro { border:1px solid #000; padding:1em; margin:1em 0; }
    </style></head><body>
      <p class="titulo">FOLHA INICIAL</p>
      <div class="quadro">
        <p><strong>Documento:</strong> ${doc.codigo}</p>
        <c:if test="${not empty doc.descrDocumento}"><p><strong>Assunto:</strong> <c:out value="${doc.descrDocumento}" /></p></c:if>
        <c:if test="${not empty doc.destinatarioString}"><p><strong>Interessado/Destinatário:</strong> <c:out value="${doc.destinatarioString}" /></p></c:if>
        <p><strong>Data:</strong> ${doc.dtExtenso}</p>
      </div>
      <c:if test="${not empty observacoesFolha}"><div>${observacoesFolha}</div></c:if>
    </body></html>
  </mod:documento>
</mod:modelo>
