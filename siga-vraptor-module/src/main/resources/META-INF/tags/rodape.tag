<%@ tag body-content="scriptless" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://localhost/jeetags" prefix="siga"%>
<%@ taglib uri="http://localhost/libstag" prefix="f"%>
<%@ attribute name="popup"%>
<%@ attribute name="pagina_de_erro"%>
<%@ attribute name="incluirJs"%>
<%@ attribute name="incluirBS" required="false"%>

<!--[if gte IE 5.5]><script language="JavaScript" src="/siga/javascript/jquery.ienav.js" type="text/javascript"></script><![endif]-->

<c:choose>
	<c:when test="${not empty sigaModalAlerta}">
		<siga:siga-modal id="sigaModalAlerta" centralizar="${sigaModalAlerta.centralizar}" abrirAoCarregarPagina="true" exibirRodape="true" 
			tituloADireita="${empty sigaModalAlerta.titulo ? 'Alerta' : sigaModalAlerta.titulo}" >
			<div class="modal-body">${sigaModalAlerta.mensagem}</div>
		</siga:siga-modal>	
	</c:when>
	<c:when test="${not empty sigaModalConfirmacao}">
		<siga:siga-modal id="sigaModalConfirmacao" centralizar="${sigaModalConfirmacao.centralizar}" abrirAoCarregarPagina="true" exibirRodape="true"  
			tituloADireita="${empty sigaModalConfirmacao.titulo ? 'Confirmação' : sigaModalConfirmacao.titulo}" 
			descricaoBotaoFechaModalDoRodape="${sigaModalConfirmacao.descricaoBotaoFechaModalDoRodape}" descricaoBotaoDeAcao="${sigaModalConfirmacao.descricaoBotaoDeAcao}" 
			linkBotaoDeAcao="${sigaModalConfirmacao.linkBotaoDeAcao}"
			inverterOrdemBotoes="${sigaModalConfirmacao.inverterBotoes}" classBotaoDeAcao="${sigaModalConfirmacao.classBotaoDeAcao}" classBotaoDeFechar="${sigaModalConfirmacao.classBotaoDeFechar}" >
				<div class="modal-body">${sigaModalConfirmacao.mensagem}</div>     	
		</siga:siga-modal>	
	</c:when>		
	<c:otherwise>
		<siga:siga-modal id="sigaModalAlerta" exibirRodape="true" tituloADireita="Alerta">
			<div class="modal-body">Mensagem de alerta</div>
		</siga:siga-modal>
	</c:otherwise>
</c:choose>
<siga:siga-spinner />

<script src="/siga/javascript/jquery/jquery-migrate-1.2.1.min.js" type="text/javascript"></script>
<script src="/siga/javascript/siga.js?v=1622040065" type="text/javascript" charset="utf-8"></script>
<script src="/siga/javascript/picketlink.js" type="text/javascript" charset="utf-8"></script>
<script src="/siga/javascript/jquery-ui-1.10.3.custom/js/jquery-ui-1.10.3.custom.min.js" type="text/javascript"></script>
<link rel="stylesheet" href="/siga/javascript/jquery-ui-1.10.3.custom/css/ui-lightness/jquery-ui-1.10.3.custom.min.css" type="text/css" media="screen, projection">
<script src="/siga/popper-1-14-3/popper.min.js"></script>

<c:if test="${empty incluirBS or incluirBS}" >
 	<script src="/siga/bootstrap/js/bootstrap.min.js?v=4.1.1" type="text/javascript"></script>
</c:if> 

<script src="/siga/javascript/datepicker-pt-BR.js" type="text/javascript"></script>

<c:if test="${not empty incluirJs}">
	<script src="${incluirJs}" type="text/javascript"></script>
</c:if>

<script type="text/javascript">
	$(document).ready(function() {
		$('.links li code').hide();
		$('.links li p').click(function() {
			$(this).next().slideToggle('fast');
		});
		$('.once').click(function(e) {
			if (this.beenSubmitted)
				e.preventDefault();
			else
				this.beenSubmitted = true;
		});
 		$('.campoData').datepicker({
           	onSelect: function(){
                   ${onSelect}
			}
		});
	});
</script>

<script>
	$('.dropdown-menu a.dropdown-toggle').on(
			'click',
			function(e) {
				if (!$(this).next().hasClass('show')) {
					$(this).parents('.dropdown-menu').first().find('.show')
							.removeClass("show");
				}
				var $subMenu = $(this).next(".dropdown-menu");
				$subMenu.toggleClass('show');

				$(this).parents('li.nav-item.dropdown.show').on(
						'hidden.bs.dropdown', function(e) {
							$('.dropdown-submenu .show').removeClass("show");
						});

				return false;
			});
</script>

<!-- Correções específicas do fluxo de edição do SIGA-EX. O arquivo existe apenas no sigaex. -->
<c:if test="${pageContext.request.contextPath eq '/sigaex'}">
	<script src="/sigaex/javascript/enfas-documento-fix.js?v=20260813" type="text/javascript" charset="utf-8"></script>
</c:if>

<!-- RODAPÉ SEM CONDICIONAL GOVSP - SEMPRE VISÍVEL (exceto popups) -->
<c:if test="${not (popup eq true or popup eq 'somenteComLogo')}">
	<footer class="text-center text-white align-middle" style="background-color: #20313b;">
		<div class="container">						
			<div class="content pt-2">
					<div class="row pt-5 align-items-center">
						<div class="col-md-4 pb-4">
							<a href="https://linksiga.trf2.jus.br" role="link" target="_Blank" class="text-decoration-none">
								<img src="/siga/imagens/logo-siga-novo-38px.png" />
								<span class="ml-2">SIGA.doc</span>
							</a>
						</div>
						<div class="col-md-4 pb-4">
							<a href="https://www.prodea.enfas.com.br/" role="link" target="_Blank">
								<img class="mx-auto d-block" src="/siga/imagens/logo-prodea-web-novo-branco.png" style="width:80%" alt="PRODEA">
							</a>
						</div>
						<div class="col-md-4 pb-4">
							<a href="https://www.enfas.com.br/" role="link" target="_Blank">
								<img class="mx-auto d-block" src="/siga/imagens/logo_enfas_colorido_rodape.png" style="width:60%" alt="Enfermagem Alessandro Silva">
							</a>
						</div>			
					</div>
			</div>
			<hr class="p-0 m-0 mb-1">			
			<div class="text-right text-white">
				<b>SIGA.doc </b>${siga_version}
			</div>
		</div>
	</footer>
</c:if>

</body>
</html>
