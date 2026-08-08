<%@ page language="java" contentType="text/html; charset=UTF-8" buffer="128kb"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%@ taglib uri="http://localhost/customtag" prefix="tags"%>
<%@ taglib uri="http://localhost/jeetags" prefix="siga"%>
<%@ taglib uri="http://localhost/functiontag" prefix="f"%>

<siga:pagina titulo="Novo Documento">
	<link rel="stylesheet" href="/siga/javascript/hierarchy-select/hierarchy-select.css" type="text/css" media="screen, projection" />
	<script type="text/javascript" src="${f:resource('/ckeditor.url')}?v=4.15.0.L0FJ.c71958523b"></script>
	<script type="text/javascript" src="../../../javascript/exDocumentoEdita.js"></script>
	<script type="text/javascript" src="/siga/javascript/jquery.blockUI.js"></script>
	<script type="text/javascript" src="/siga/javascript/hierarchy-select/hierarchy-select.js"></script>
	<script type="text/javascript" src="/siga/javascript/crypto-js/4.1.1/crypto-js.min.js"></script>
	<script type="text/javascript" src="/siga/javascript/crypto-js/4.1.1/sha256.min.js"></script>

	<link rel="stylesheet" href="/siga/javascript/select2/select2.css" type="text/css" media="screen, projection" />
	<link rel="stylesheet" href="/siga/javascript/select2/select2-bootstrap.css" type="text/css" media="screen, projection" />

	<c:set var="timeoutMod" scope="session" value="${f:resource('/siga.session.modelos.tempo.expiracao')}" />
	<c:set var="urlSigaArq" scope="session" value="${f:resource('/sigaarq.url')}" />
	<div class="container-fluid">
		
		<c:if test="${not empty mensagem}">
			<div class="row">
				<div class="col-sm-12">
					<p id="mensagem" class="alert alert-warning">
						<fmt:message key="${mensagem}" />
					</p>
					<script>
						setTimeout(function() {
							$('#mensagem').fadeTo(1000, 0, function() {
								$('#mensagem').slideUp(1000);
							});
						}, 5000);
					</script>
				</div>
			</div>
		</c:if>
		<div class="card bg-light mb-3">
			<div class="card-header">
				<h5>
					<c:choose>
						<c:when test='${empty exDocumentoDTO.doc}'>
							Novo Documento
						</c:when>
						<c:otherwise>
							<span id="codigoDoc">${exDocumentoDTO.doc.codigo}</span>
						</c:otherwise>
					</c:choose>
				</h5>
			</div>
			<div class="card-body">
				<form id="frm" name="frm" theme="simple" method="post" enctype="multipart/form-data" class="mb-0">
					<!-- Campos ocultos -->
					<input type="hidden" id="idTamanhoMaximoDescricao" name="exDocumentoDTO.tamanhoMaximoDescricao" value="${exDocumentoDTO.tamanhoMaximoDescricao}" />
					<input type="hidden" id="alterouModelo" name="exDocumentoDTO.alterouModelo" />
					<input type="hidden" id="clickSelect" name="clickSelect" />
					<input type="hidden" id="hasPai" name="hasPai" value="${hasPai}" />
					<input type="hidden" id="isPaiEletronico" name="isPaiEletronico" value="${isPaiEletronico}" />
					<input type="hidden" name="postback" value="1" />
					<input type="hidden" id="sigla" name="exDocumentoDTO.sigla" value="${exDocumentoDTO.sigla}" />
					<input type="hidden" name="exDocumentoDTO.nomePreenchimento" value="" />
					<input type="hidden" name="campos" value="criandoAnexo" />
					<input type="hidden" name="campos" value="criandoSubprocesso" />
					<input type="hidden" name="campos" value="autuando" />
					<input type="hidden" name="exDocumentoDTO.autuando" value="${exDocumentoDTO.autuando}" />
					<input type="hidden" name="exDocumentoDTO.criandoAnexo" value="${exDocumentoDTO.criandoAnexo}" />
					<input type="hidden" name="exDocumentoDTO.criandoSubprocesso" value="${exDocumentoDTO.criandoSubprocesso}" />
					<input type="hidden" name="campos" value="idMobilAutuado" />
					<input type="hidden" name="exDocumentoDTO.idMobilAutuado" value="${exDocumentoDTO.idMobilAutuado}" />
					<input type="hidden" name="exDocumentoDTO.id" value="${exDocumentoDTO.doc.idDoc}" />
					<input type="hidden" name="exDocumentoDTO.idMod.original" value="${exDocumentoDTO.modelo.idMod}" />
					<input type="hidden" name="cliente" id="cliente" value="${siga_cliente}" />
					<input type="hidden" id="visualizador" value="${f:resource('/sigaex.pdf.visualizador') }" />
					<input type="hidden" id="adicionarRestricaoAcessoAntes" name="adicionarRestricaoAcessoAntes" value="false" />
					<input type="hidden" id="gravarAssinar" name="exDocumentoDTO.assinar" value="false" />
					<input type="hidden" id="fecharDoc" name="exDocumentoDTO.fechar" value="false" />
					
					<input type="hidden" name="exDocumentoDTO.idTpDoc" value="${exDocumentoDTO.idTpDoc}" />
					<input type="hidden" name="exDocumentoDTO.eletronico" value="${exDocumentoDTO.eletronico}" />
					<input type="hidden" name="campos" value="idTpDoc" />

					<!-- Modelo -->
					<div class="row">
						<div class="col col-12 col-lg-8">
							<div class="form-group">
								<label for="modelos-select">Modelo</label>
								<div class="btn-group hierarchy-select form-control p-0 div-width-min0" data-resize="auto" id="modelos-select" style="min-width: 0px !important;">
									<button type="button" class="btn btn-light dropdown-toggle bg-white" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" data-disabled="true">
										<span class="selected-label pull-left">&nbsp;</span>
									</button>
									<div class="dropdown-menu form-control" aria-labelledby="dropdownMenuButton">
										<div class="hs-searchbox">
											<input type="text" class="form-control" autocomplete="off" placeholder="Pesquisar modelo...">
										</div>
										<ul id="ulmod" class="dropdown-menu show inner" role="menu"></ul>
									</div>
									<input class="hidden hidden-field" name="exDocumentoDTO.idMod" readonly="readonly" onchange="alterouModeloSelect()" aria-hidden="true" type="text" value="${exDocumentoDTO.idMod}" />
								</div>
								<small class="form-text text-muted"><fmt:message key="documento.help.modelo" /></small>
							</div>
							<c:if test='${exDocumentoDTO.tipoDocumento == "externo" }'>
								<input type="hidden" name="exDocumentoDTO.idMod" value="${exDocumentoDTO.idMod}" />
							</c:if>
						</div>

						<c:if test='${ exDocumentoDTO.tipoDocumento == "interno"  && !ehPublicoExterno}'>
							<div class="col col-12 col-lg-4">
								<div class="form-group">
									<label data-toggle="tooltip" title="Preenchimento automático com dados padrão para agilizar a criação.">
										<fmt:message key="documento.preenchimento.automatico" />
									</label>
									<div class="input-group">
										<select id="preenchimento" name="exDocumentoDTO.preenchimento" onchange="javascript:carregaPreench()" class="xform-control xsiga-select2 custom-select">
											<c:forEach items="${exDocumentoDTO.preenchimentos}" var="item">
												<option value="${item.idPreenchimento}" ${item.idPreenchimento == exDocumentoDTO.preenchimento ? 'selected' : ''}>${item.descricaoNaLista(lotaTitular)}</option>
											</c:forEach>
										</select>
										<div class="input-group-append">
											<c:if test="${empty exDocumentoDTO.preenchimento or exDocumentoDTO.preenchimento==0}">
												<c:set var="desabilitaBtn">d-none</c:set>
											</c:if>
											<button type="button" name="btnAlterar" onclick="javascript:alteraPreench()" class="btn btn-sm btn-secondary p-2 ${desabilitaBtn}" title="Gravar alterações">
												<i class="far fa-edit"></i>
											</button>
											<button type="button" name="btnRemover" onclick="javascript:removePreench()" class="btn btn-sm btn-secondary p-2 ${desabilitaBtn}" title="Remover este item">
												<i class="far fa-trash-alt"></i>
											</button>
											<button type="button" name="btnAdicionar" onclick="javascript:adicionaPreench()" class="btn btn-sm btn-secondary p-2" title="Criar um novo">
												<i class="fas fa-plus"></i>
											</button>
										</div>
									</div>
								</div>
							</div>
						</c:if>
					</div>

					<!-- Acesso e Data -->
					<div class="row">
						<div class="col-sm-3">
							<div class="form-group">
								<input type="hidden" name="campos" value="nivelAcesso" /> 
								<label for="exDocumentoDTO.nivelAcesso">Acesso</label>
								<select name="exDocumentoDTO.nivelAcesso" class="form-control">
									<c:forEach items="${exDocumentoDTO.listaNivelAcesso}" var="item">
										<option value="${item.idNivelAcesso}" ${item.idNivelAcesso == exDocumentoDTO.nivelAcesso ? 'selected' : ''}>${item.nmNivelAcesso}</option>
									</c:forEach>
								</select>
								<small class="form-text text-muted">Selecione o nível de acesso do documento.</small>
							</div>
						</div>
						<div class="col-sm-3">
							<div class="form-group">
								<label for="exDocumentoDTO.dtDocString">Data <span class="text-danger">*</span></label>
								<input type="text" name="exDocumentoDTO.dtDocString" size="10" onblur="javascript:verifica_data(this, true);" value="${exDocumentoDTO.dtDocString}" class="form-control campoData" autocomplete="off" id="dataAtual" readonly="readonly" />
								<small class="form-text text-muted">Data preenchida automaticamente.</small>
							</div>
						</div>
					</div>

					<c:if test='${exDocumentoDTO.tipoDocumento == "antigo"}'>
						<div class="row">
							<div class="col-sm-2">
								<div class="form-group">
									<label for="exDocumentoDTO.numExtDoc">Nº original</label>
									<input type="text" name="exDocumentoDTO.numExtDoc" size="16" maxLength="32" value="${exDocumentoDTO.numExtDoc}" class="form-control" />
								</div>
							</div>
							<div class="col-sm-4">
								<div class="form-group">
									<label for="exDocumentoDTO.numAntigoDoc">Nº antigo</label>
									<input type="text" name="exDocumentoDTO.numAntigoDoc" size="16" maxLength="32" value="${exDocumentoDTO.numAntigoDoc}" class="form-control" />
									<small class="form-text text-muted">(informar o número do documento no antigo sistema).</small>
								</div>
							</div>
						</div>
					</c:if>

					<!-- Subscritor e switches -->
					<c:choose>
						<c:when test='${exDocumentoDTO.tipoDocumento == "externo" or exDocumentoDTO.tipoDocumento == "externo_capturado" or exDocumentoDTO.tipoDocumento == "externo_capturado_formato_livre"}'>
						</c:when>
						<c:otherwise>
							<div class="row js-siga-sp-documento-analisa-alteracao">
								<c:choose>
									<c:when test="${!ehPublicoExterno}">
										<div class="col-sm-7">
											<div class="form-group">
												<input type="hidden" name="campos" value="subscritorSel.id" />
												<input type="hidden" name="campos" value="substituicao" />
												<input type="hidden" name="campos" value="personalizacao" />
												<input type="hidden" id="temCossignatarios" value="${not empty exDocumentoDTO.doc.cosignatarios}" />
												<label>Responsável pela Assinatura <span class="text-danger">*</span></label>
												<siga:selecao propriedade="subscritor" inputName="exDocumentoDTO.subscritor" modulo="siga" tema="simple" />
												<small class="form-text text-muted">Selecione a pessoa responsável pela assinatura do documento.</small>
											</div>
										</div>
										<div class="col-sm-5 d-flex align-items-center">
											<div class="form-check form-check-inline">
												<input type="checkbox" name="exDocumentoDTO.substituicao" class="form-check-input" id="substitutoSwitch" onclick="javascript:displayTitular(this);" <c:if test="${exDocumentoDTO.substituicao}">checked</c:if> />
												<label class="form-check-label" for="substitutoSwitch">
													Substituto
													<i class="fas fa-info-circle text-secondary ml-1" data-toggle="tooltip" data-trigger="hover" data-placement="top" title="Marque se o responsável pela assinatura é um substituto. Ao marcar, aparecerá o campo 'Titular' para indicar quem está sendo substituído."></i>
												</label>
												<input type="checkbox" name="exDocumentoDTO.personalizacao" class="form-check-input ml-3" id="personalizacaoSwitch" onclick="javascript:displayPersonalizacao(this);" <c:if test="${exDocumentoDTO.personalizacao}">checked</c:if> />
												<label class="form-check-label" for="personalizacaoSwitch">
													Personalizar
													<i class="fas fa-info-circle text-secondary ml-1" data-toggle="tooltip" data-trigger="hover" data-placement="top" title="Permite personalizar a exibição do nome, função, lotação e cidade na assinatura do documento."></i>
												</label>
												<input type="checkbox" class="form-check-input ml-3" id="cossignatariosSwitch" onclick="javascript:displayCossignatarios(this);" <c:if test="${not empty exDocumentoDTO.doc.cosignatarios}">checked</c:if> />
												<label class="form-check-label" for="cossignatariosSwitch">
													Cossignatários
													<i class="fas fa-info-circle text-secondary ml-1" data-toggle="tooltip" data-trigger="hover" data-placement="top" title="Marque para adicionar outros assinantes (cossignatários) que também devem assinar o documento em conjunto."></i>
												</label>
											</div>
										</div>
									</c:when>
									<c:otherwise>
										<div class="col-sm-12">
											<label><fmt:message key="documento.subscritor" /> <span class="text-danger">*</span></label>
											<div class="row">
												<div class="col-sm-4">
													<input type="text" value="${exDocumentoDTO.subscritorSel.sigla}" class="form-control" disabled />
												</div>
												<div class="col-sm-8">
													<input type="text" value="${exDocumentoDTO.subscritorSel.descricao}" class="form-control" disabled />
												</div>
											</div>
										</div>
									</c:otherwise>
								</c:choose>
							</div>
						</c:otherwise>
					</c:choose>

					<div class="row js-siga-sp-documento-analisa-alteracao mt-1" id="divCossignatarios" style="display: ${not empty exDocumentoDTO.doc.cosignatarios ? '' : 'none'};">
						<div class="col-sm-8">
							<div class="form-group">
								<label>Outros Assinantes / Cossignatários (Opcional)</label>
								<siga:selecao propriedade="cosignatario" inputName="exDocumentoDTO.cosignatario" modulo="siga" tema="simple" />
								<small class="form-text text-muted">Selecione pessoas adicionais para assinarem em conjunto.</small>
							</div>
						</div>
					</div>

					<input type="hidden" name="campos" value="titularSel.id" />
					<div id="tr_titular" style="display: ${exDocumentoDTO.substituicao ? '' : 'none'};">
						<div class="row js-siga-sp-documento-analisa-alteracao">
							<div class="col-sm-8">
								<div class="form-group">
									<label>Substituto do Responsável pela Assinatura <span class="text-danger">*</span></label>
									<siga:selecao propriedade="titular" inputName="exDocumentoDTO.titular" tema="simple" modulo="siga" />
								</div>
							</div>
						</div>
					</div>

					<input type="hidden" name="campos" value="nmFuncaoSubscritor" />
					<input type="hidden" name="exDocumentoDTO.nmFuncaoSubscritor" maxlength="128" id="frm_nmFuncaoSubscritor" value="${exDocumentoDTO.nmFuncaoSubscritor}" />
					<div id="tr_personalizacao" style="display: ${exDocumentoDTO.personalizacao ? '' : 'none'};">
						<div class="row ml-1"><h6>Personalização</h6></div>
						<div class="row js-siga-sp-documento-analisa-alteracao">
							<div class="col-sm-2"><div class="form-group"><label>Função</label><input type="text" id="personalizarFuncao" maxlength="125" class="form-control"></div></div>
							<div class="col-sm-2"><div class="form-group"><label>Lotação</label><input type="text" id="personalizarUnidade" maxlength="125" class="form-control"></div></div>
							<div class="col-sm-2"><div class="form-group"><label>Cidade</label><input type="text" id="personalizarLocalidade" maxlength="125" class="form-control"></div></div>
							<div class="col-sm-4"><div class="form-group"><label>Nome</label><input type="text" id="personalizarNome" maxlength="125" class="form-control"></div></div>
						</div>
					</div>

					<!-- Destinatário -->
					<c:if test="${not empty exDocumentoDTO.listaTipoDest}">
						<div class="row">
							<div class="col-sm-2">
								<div class="form-group">
									<label>Destinatário <span class="text-danger">*</span></label>
									<select name="exDocumentoDTO.tipoDestinatario" onchange="javascript:sbmt();" class="form-control">
										<c:forEach items="${exDocumentoDTO.listaTipoDest}" var="item">
											<option value="${item.key}" ${item.key == exDocumentoDTO.tipoDestinatario ? 'selected' : ''}>${item.value}</option>
										</c:forEach>
									</select>
								</div>
							</div>
							<div class="col-sm-6">
								<div class="form-group">
									<label>&nbsp;</label>
									<siga:span id="destinatario" depende="tipoDestinatario">
										<c:choose>
											<c:when test='${exDocumentoDTO.tipoDestinatario == 1}'>
												<input type="hidden" name="campos" value="destinatario" />
												<siga:selecao propriedade="destinatario" inputName="exDocumentoDTO.destinatario" tema="simple" idAjax="destinatario1" reler="ajax" modulo="siga" />
											</c:when>
											<c:when test='${exDocumentoDTO.tipoDestinatario == 2}'>
												<input type="hidden" name="campos" value="lotacaoDestinatarioSel.id" />
												<siga:selecao propriedade="lotacaoDestinatario" inputName="exDocumentoDTO.lotacaoDestinatario" tema="simple" idAjax="destinatario2" reler="ajax" modulo="siga" onchangeid="updateURL()" />
											</c:when>
											<c:when test='${exDocumentoDTO.tipoDestinatario == 3}'>
												<input type="hidden" name="campos" value="orgaoExternoDestinatarioSel.id" />
												<siga:selecao propriedade="orgaoExternoDestinatario" inputName="exDocumentoDTO.orgaoExternoDestinatario" tema="simple" idAjax="destinatario3" reler="ajax" modulo="siga" />
											</c:when>
											<c:otherwise>
												<input type="hidden" name="campos" value="nmDestinatario" />
												<input type="text" name="exDocumentoDTO.nmDestinatario" size="80" maxLength="256" value="${exDocumentoDTO.nmDestinatario}" class="form-control w-100" />
											</c:otherwise>
										</c:choose>
									</siga:span>
								</div>
							</div>
							<c:if test='${exDocumentoDTO.tipoDestinatario == 3}'>
								<div class="col-sm-3">
									<div class="form-group">
										<label>&nbsp;</label>
										<input type="text" name="exDocumentoDTO.nmOrgaoExterno" size="120" maxLength="256" value="${exDocumentoDTO.nmOrgaoExterno}" class="form-control w-100" />
									</div>
								</div>
							</c:if>
						</div>
					</c:if>

					<!-- Classificação -->
					<div class="row">
						<div class="col col-5">
							<div class="form-group">
								<input type="hidden" name="campos" value="classificacaoSel.id" />
								<label>Classificação Documental <span class="text-danger">*</span></label>
								<siga:span id="classificacao" depende="forma;modelo">
									<siga:selecao modulo="sigaex" propriedade="classificacao" inputName="exDocumentoDTO.classificacao" urlAcao="buscar" urlSelecionar="selecionar" tema="simple" onchangeid="updateURL()" />
								</siga:span>
							</div>
						</div>
					</div>
					<c:if test="${exDocumentoDTO.classificacaoSel.id != null && exDocumentoDTO.classificacaoIntermediaria}">
						<div class="row">
							<div class="col-4">
								<div class="form-group">
									<label>Descrição da Classificação</label>
									<siga:span id="descrClassifNovo" depende="forma;modelo;classificacao">
										<input type="text" name="exDocumentoDTO.descrClassifNovo" size="80" value="${exDocumentoDTO.descrClassifNovo}" maxLength="4000" class="form-control" />
									</siga:span>
								</div>
							</div>
						</div>
					</c:if>

					<!-- Assunto -->
					<div class="row js-siga-sp-documento-analisa-alteracao" id="divAssunto">
						<div class="col-sm-8">
							<div class="form-group">
								<label>Assunto <span class="text-danger">*</span></label>
								<textarea name="exDocumentoDTO.descrDocumento" cols="80" rows="2" id="descrDocumento" class="form-control" oninput="updateURL()">${exDocumentoDTO.descrDocumento}</textarea>
								<small class="form-text text-muted">(preencher com palavras-chave, substantivos, masculino, singular).</small>
							</div>
						</div>
					</div>

					<!-- Arquivo -->
					<c:if test='${podeTrocarPdfCapturado}'>
						<div class="row js-siga-sp-documento-analisa-alteracao">
							<div class="col">
								<div class="form-group">
									<br>
									<div class="form-group" style="margin-bottom: 0">
										<c:choose>
											<c:when test="${!exDocumentoDTO.capturadoFormatoLivre}">
												<div class="custom-file">
													<input type="file" class="custom-file-input" id="arquivo" name="arquivo" accept="application/pdf" onchange="testpdf(this.form, ${tamanhoMaximoArquivo})" title="arquivo">
													<label class="custom-file-label" for="arquivo" data-toggle="tooltip" title="Selecione o arquivo PDF do documento."><i class="far fa-file-pdf"></i>&nbsp;&nbsp;Arquivo (limite de ${tamanhoMaximoArquivo/1024/1024}MB)</label>
													<div class="invalid-feedback invalid-feedback-arquivo">Selecione o arquivo</div>
												</div>
											</c:when>
											<c:otherwise>
												<script type="text/javascript" src="/siga/javascript/siga-arquivo.js"></script>
												<input type='hidden' name='vars' class='uploadclass' value='tokenArquivo'>
												<input type='hidden' id='tokenArquivo' name='tokenArquivo'>
												<div class="custom-file ${exDocumentoDTO.cpArquivoFormatoLivre.nomeArquivo == null && tokenArquivo == null ? '' : 'd-none'} col-lg-8">
													<c:set var="extensoes" value="${fn:split(dateString, ',')}" />
													<input type="file" class="custom-file-input" id="arqUpload" name="arqUpload" accept="${exDocumentoDTO.modelo.extensoesArquivoComPonto}" onchange="uploadArq('${urlSigaArq}/api/v1/', this, ${tamanhoMaximoArquivoFormatoLivre});" title="arqUpload">
													<label class="custom-file-label" for="arqUpload" data-toggle="tooltip" title="Selecione o arquivo (formatos permitidos conforme o modelo)."><i class="far fa-file-pdf"></i>&nbsp;&nbsp;Arquivo (limite de ${tamanhoMaximoArquivoFormatoLivre/1024/1024/1024}GB)</label>
												</div>
												<div id="barraProgresso" name="barraProgresso" class="d-none mt-2">
													<small id="msgProgressBar" class="text-muted"></small>
													<div class="progress">
														<div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
													</div>
													<button type="button" class="btn btn-sm btn-primary mt-1" onclick="abortarUpload();">Cancelar</button>
												</div>
												<div class="${exDocumentoDTO.cpArquivoFormatoLivre.nomeArquivo != null || tokenArquivo != null ? '' : 'd-none'} row">
													<div id="linkArquivoDiv" class="col-lg-8">
														<div class="form-group">
															<label for="linkArquivo" class="title">Arquivo</label>
															<div id="linkArquivo" class="form-control" disabled read-only><i class="far fa-file-pdf mr-2"></i>${exDocumentoDTO.cpArquivoFormatoLivre.nomeArquivo}</div>
														</div>
													</div>
													<div class="col-sm">
														<button id="btnResetaArq" class='btn btn-secondary mt-lg-4' onclick='removerArq()'>Limpar</button>
													</div>
												</div>
												<small class="form-text text-muted">Tipos permitidos: ${exDocumentoDTO.modelo.extensoesArquivoComPonto}</small>
												<div class="invalid-feedback invalid-feedback-arqUpload"></div>
											</c:otherwise>
										</c:choose>
									</div>
								</div>
							</div>
						</div>
					</c:if>

					<c:if test='${exDocumentoDTO.tipoDocumento == "externo"}'>
						<div class="row"><h6>Dados do Documento Original</h6></div>
						<div class="row js-siga-sp-documento-analisa-alteracao">
							<input type="hidden" name="campos" value="dtDocOriginalString" />
							<input type="hidden" name="campos" value="numExtDoc" />
							<div class="col-sm-2"><div class="form-group"><label>Nº original</label><input type="text" name="exDocumentoDTO.numExtDoc" size="32" maxLength="32" value="${exDocumentoDTO.numExtDoc}" class="form-control" /></div></div>
							<div class="col-sm-2"><div class="form-group"><label>Data</label><input type="text" name="exDocumentoDTO.dtDocOriginalString" size="10" onblur="javascript:verifica_data(this, true);" value="${exDocumentoDTO.dtDocOriginalString}" class="form-control" /></div></div>
							<div class="col-sm-2"><div class="form-group"><input type="hidden" name="campos" value="numAntigoDoc" /><label>Nº antigo</label><input type="text" name="exDocumentoDTO.numAntigoDoc" size="32" maxLength="34" value="${exDocumentoDTO.numAntigoDoc}" /></div></div>
						</div>
						<div class="row js-siga-sp-documento-analisa-alteracao">
							<div class="col-sm-2"><div class="form-group"><label>Emitente</label><select name="exDocumentoDTO.tipoEmitente" onchange="javascript:sbmt();" class="form-control"><c:forEach items="${exDocumentoDTO.listaTipoEmitente}" var="item"><option value="${item.key}" ${item.key == exDocumentoDTO.tipoEmitente ? 'selected' : ''}>${item.value}</option></c:forEach></select></div></div>
							<div class="col-sm-4"><div class="form-group"><siga:span id="emitente"><c:choose><c:when test='${exDocumentoDTO.tipoEmitente == 1}'><input type="hidden" name="campos" value="cpOrgaoSel.id" /><siga:selecao propriedade="cpOrgao" inputName="exDocumentoDTO.cpOrgao" tema="simple" modulo="siga" /><label><fmt:message key="documento.subscritor" /></label><input type="hidden" name="campos" value="nmSubscritorExt" /><input type="text" name="exDocumentoDTO.nmSubscritorExt" size="30" maxLength="256" value="${exDocumentoDTO.nmSubscritorExt}" class="form-control" /></c:when><c:when test='${exDocumentoDTO.tipoEmitente == 2}'><input type="hidden" name="campos" value="obsOrgao" /><input type="text" size="30" name="exDocumentoDTO.obsOrgao" maxLength="256" value="${exDocumentoDTO.obsOrgao}" class="form-control mt-4" /></c:when></c:choose></siga:span></div></div>
						</div>
					</c:if>

					<!-- ENTREVISTA / CAMPOS EXTRAS DO MODELO -->
					<c:if test='${exDocumentoDTO.tipoDocumento == "interno" or exDocumentoDTO.capturado}'>
						<c:if test="${exDocumentoDTO.modelo.conteudoTpBlob == 'template/freemarker' or not empty exDocumentoDTO.modelo.nmArqMod}">
							<div class="row">
								<div class="col-sm">
									<siga:span id="spanEntrevista" depende="tipoDestinatario;destinatario;forma;modelo">
										<c:if test="${exDocumentoDTO.modelo.conteudoTpBlob == 'template/freemarker'}">
											${f:processarModelo(exDocumentoDTO.doc, 'entrevista', par, exDocumentoDTO.preenchRedirect)}
										</c:if>
										<c:if test="${exDocumentoDTO.modelo.conteudoTpBlob != 'template/freemarker'}">
											<c:import url="/paginas/expediente/modelos/${exDocumentoDTO.modelo.nmArqMod}?entrevista=1" />
										</c:if>
									</siga:span>
								</div>
							</div>
						</c:if>
					</c:if>

					<!-- BOTÕES -->
					<div class="row mt-4">
						<div class="col-sm-8">
							<button id="btnGravar" type="button" onclick="javascript: gravarDoc(); return false;" name="gravar" class="btn btn-primary" accesskey="g" title="Apenas grava o documento podendo continuar a Edição">
								<i class="fas fa-save"></i> <u>G</u>ravar
							</button>
							&nbsp;
							<button id="btnFinalizarAssinar" type="button" onclick="javascript: gravarAssinarDoc(); return false;" name="finalizareGravar" class="btn btn-success" accesskey="f" title="Finalizar documento em definitivo e em seguida realizar assinatura digital">
								<i class="fas fa-check-circle"></i> <u>F</u>inalizar e Assinar
							</button>
							&nbsp;
							<button type="button" name="ver_doc" onclick="javascript: popitup_documento(false); return false;" class="btn btn-info" accesskey="v" title="Visualizar o documento gerado">
								<i class="fas fa-file-alt"></i> <u>V</u>er Documento
							</button>
							&nbsp;
							<button type="button" name="ver_doc_pdf" onclick="javascript: popitup_documento(true); return false;" class="btn btn-secondary" accesskey="i" title="Visualizar versão para impressão (PDF)">
								<i class="fas fa-print"></i> Ver <u>I</u>mpressão
							</button>
							&nbsp;
							<button type="button" name="voltar" onclick="javascript: history.back();" class="btn btn-outline-dark" accesskey="r" title="Voltar à página anterior">
								<i class="fas fa-arrow-left"></i> Volta<u>r</u>
							</button>
						</div>
					</div>
				</form>
			</div>
		</div>
	</div>

	<script type="text/javascript" src="../../../javascript/documento.validacao.js?v=1664993973"></script>
</siga:pagina>

<script type="text/javascript">
	
	function displayPersonalizacao(thisElement) {
		var thatElement = document.getElementById('tr_personalizacao');
		if (thisElement.checked)
			thatElement.style.display = '';
		else {
			thatElement.style.display = 'none';
			document.getElementById('personalizarFuncao').value = '';
			document.getElementById('personalizarUnidade').value = '';
		}
	}

	function displayCossignatarios(thisElement) {
		var div = document.getElementById('divCossignatarios');
		if (thisElement.checked) {
			div.style.display = '';
		} else {
			div.style.display = 'none';
			var hiddenInput = document.querySelector('input[name="exDocumentoDTO.cosignatario"]');
			if (hiddenInput) hiddenInput.value = '';
			var displaySpan = document.querySelector('#cosignatarioSelect + .siga-selecao-display');
			if (displaySpan) displaySpan.innerHTML = '';
		}
	}

	function personalizacaoSeparar() {
		var a = document.getElementById('frm_nmFuncaoSubscritor').value.split(';');
		document.getElementById('personalizarFuncao').value = a.length > 0 ? a[0] : '';
		document.getElementById('personalizarUnidade').value = a.length > 1 ? a[1] : '';
		document.getElementById('personalizarLocalidade').value = a.length > 2 ? a[2] : '';
		document.getElementById('personalizarNome').value = a.length > 3 ? a[3] : '';
	}

	function personalizacaoJuntar() {
		var f = document.getElementById('personalizarFuncao').value.trim();
		var u = document.getElementById('personalizarUnidade').value.trim();
		var l = document.getElementById('personalizarLocalidade').value.trim();
		var n = document.getElementById('personalizarNome').value.trim();
		var j = f + ';' + u + ';' + l + ';' + n;
		while (j.slice(-1) == ';')
			j = j.substring(0, j.length - 1);
		document.getElementById('frm_nmFuncaoSubscritor').value = j;
	}

	function sbmt(id) {
		var frm = document.getElementById('frm');
		var mod = document.getElementsByName('exDocumentoDTO.idMod')[0];
		if (mod.value == '[Selecione]')
			mod.value = '0';
		if (id && typeof ReplaceInnerHTMLFromAjaxResponse === 'function') {
			ReplaceInnerHTMLFromAjaxResponse('recarregar', frm, id);
		} else {
			frm.action = id !== 'undefined' ? 'recarregar' : 'editar?modelo=' + document.getElementsByName('exDocumentoDTO.idMod')[0].value;
			frm.submit();
		}
	}

	// ===== FUNÇÃO PARA OBTER RÓTULO DOS CAMPOS =====
	function obterRotuloCampo(campo) {
		if (campo.id) {
			var label = document.querySelector('label[for="' + campo.id + '"]');
			if (label) return label.innerText.trim().replace(/\*/g, '').trim();
		}
		var parent = campo.closest ? campo.closest('.form-group, .col-sm, .row, .col') : null;
		if (parent) {
			var labelParent = parent.querySelector('label');
			if (labelParent) return labelParent.innerText.trim().replace(/\*/g, '').trim();
		}
		var container = campo.closest ? campo.closest('.siga-selecao-container, .form-group') : null;
		if (container) {
			var lbl = container.querySelector('label');
			if (lbl) return lbl.innerText.trim().replace(/\*/g, '').trim();
		}
		if (campo.name) {
			var partes = campo.name.split('.');
			var nome = partes[partes.length - 1];
			return nome.replace(/([A-Z])/g, ' $1').trim() || campo.id || 'Campo';
		}
		return campo.id || 'Campo não identificado';
	}

	// ===== VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS =====
	function validarTodosCamposObrigatorios() {
		var erros = [];
		var form = document.getElementById('frm');
		if (!form) return ['Formulário não encontrado'];

		// 1. Campos com required
		var requiredFields = form.querySelectorAll('[required]');
		for (var i = 0; i < requiredFields.length; i++) {
			var field = requiredFields[i];
			if (field.offsetParent === null || field.style.display === 'none' || field.disabled) continue;
			var valor = field.value;
			var rotulo = obterRotuloCampo(field);
			if (field.tagName === 'SELECT') {
				if (!valor || valor === '' || valor === '0' || valor === '[Selecione]' || valor === 'Selecione...') {
					erros.push(rotulo);
				}
			} else if (field.type === 'checkbox' || field.type === 'radio') {
				var nome = field.name;
				if (nome) {
					var grupo = form.querySelectorAll('input[name="' + nome + '"]');
					var marcado = false;
					for (var j = 0; j < grupo.length; j++) {
						if (grupo[j].checked) { marcado = true; break; }
					}
					if (!marcado) erros.push(rotulo);
				} else if (!field.checked) {
					erros.push(rotulo);
				}
			} else {
				if (!valor || valor.trim() === '') {
					erros.push(rotulo);
				}
			}
		}

		// 2. Campos do modelo com data-obrigatorio
		var camposModelo = form.querySelectorAll('[data-obrigatorio="true"]');
		for (var k = 0; k < camposModelo.length; k++) {
			var campo = camposModelo[k];
			if (campo.offsetParent === null || campo.style.display === 'none' || campo.disabled) continue;
			var valorCampo = campo.value;
			var rotuloCampo = obterRotuloCampo(campo) || 'Campo do modelo';
			if (campo.tagName === 'SELECT') {
				if (!valorCampo || valorCampo === '' || valorCampo === '0' || valorCampo === '[Selecione]') {
					erros.push(rotuloCampo);
				}
			} else if (campo.type === 'checkbox' || campo.type === 'radio') {
				var nomeGrupo = campo.name;
				if (nomeGrupo) {
					var grupo = form.querySelectorAll('input[name="' + nomeGrupo + '"]');
					var marcado = false;
					for (var l = 0; l < grupo.length; l++) {
						if (grupo[l].checked) { marcado = true; break; }
					}
					if (!marcado) erros.push(rotuloCampo);
				} else if (!campo.checked) {
					erros.push(rotuloCampo);
				}
			} else {
				if (!valorCampo || valorCampo.trim() === '') {
					erros.push(rotuloCampo);
				}
			}
		}

		return erros;
	}

	// ===== EXIBE MODAL USANDO O SIGA =====
	function exibirModalErro(mensagem) {
		// Se existir o sigaModal, usa ele
		if (typeof sigaModal !== 'undefined' && typeof sigaModal.alerta === 'function') {
			sigaModal.alerta(mensagem);
			return;
		}

		// Fallback: cria um modal Bootstrap manualmente
		var modalId = 'modalValidacao';
		var modalExistente = document.getElementById(modalId);
		if (modalExistente) modalExistente.remove();

		// CORREÇÃO: substitui as quebras de linha em JavaScript puro
		var mensagemHtml = mensagem.replace(/\n/g, '<br>');
		var modalHtml = `
			<div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-hidden="true">
				<div class="modal-dialog" role="document">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title">Alerta</h5>
							<button type="button" class="close" data-dismiss="modal" aria-label="Fechar">
								<span aria-hidden="true">&times;</span>
							</button>
						</div>
						<div class="modal-body">
							${mensagemHtml}
						</div>
						<div class="modal-footer">
							<button type="button" class="btn btn-primary" data-dismiss="modal">Fechar</button>
						</div>
					</div>
				</div>
			</div>
		`;
		$('body').append(modalHtml);
		$('#' + modalId).modal('show');
	}

	// ===== FUNÇÃO GRAVAR =====
	function gravarDoc() {
		if (typeof sincronizarEditoresDinamicos === 'function') {
			sincronizarEditoresDinamicos();
		}

		var erros = validarTodosCamposObrigatorios();
		if (erros.length > 0) {
			var msg = 'Os seguintes campos obrigatórios precisam ser preenchidos:\n\n' + erros.join('\n');
			exibirModalErro(msg);
			return false;
		}

		personalizacaoJuntar();

		if (typeof gravar === 'function') {
			gravar(false);
			return;
		}

		document.getElementById('gravarAssinar').value = 'false';
		document.getElementById('fecharDoc').value = 'false';
		var frm = document.getElementById('frm');
		if (frm) {
			frm.action = 'gravar?redirect=listar';
			frm.submit();
		} else {
			exibirModalErro('Erro: formulário não encontrado.');
		}
	}

	// ===== FUNÇÃO FINALIZAR E ASSINAR =====
	function gravarAssinarDoc() {
		if (typeof sigaSpinner !== 'undefined' && sigaSpinner.mostrar) sigaSpinner.mostrar();

		if (typeof sincronizarEditoresDinamicos === 'function') {
			sincronizarEditoresDinamicos();
		}

		var erros = validarTodosCamposObrigatorios();
		if (erros.length > 0) {
			var msg = 'Os seguintes campos obrigatórios precisam ser preenchidos antes de finalizar:\n\n' + erros.join('\n');
			exibirModalErro(msg);
			if (typeof sigaSpinner !== 'undefined' && sigaSpinner.ocultar) sigaSpinner.ocultar();
			return false;
		}

		sessionStorage.setItem('redirecionarParaAssinatura', 'true');
		var siglaAtual = document.getElementById('codigoDoc') ? document.getElementById('codigoDoc').innerHTML.trim() : '';
		if (siglaAtual && siglaAtual !== 'Novo Documento' && siglaAtual !== 'NOVO') {
			sessionStorage.setItem('siglaParaAssinar', siglaAtual);
		}

		if (typeof gravar === 'function') {
			gravar(true);
			return;
		}

		document.getElementById('gravarAssinar').value = 'true';
		document.getElementById('fecharDoc').value = 'true';
		var frm = document.getElementById('frm');
		if (frm) {
			frm.action = 'gravar';
			frm.submit();
		}
	}

	function popitup_documento(pdf) {
		var frm = document.getElementById('frm');
		if (!frm) return;
		personalizacaoJuntar();
		var popW = 900, popH = 700;
		var winleft = (screen.width - popW) / 2;
		var winUp = (screen.height - popH) / 2;
		var winProp = 'width=' + popW + ',height=' + popH + ',left=' + winleft + ',top=' + winUp + ',scrollbars=yes,resizable';
		var win = window.open('', 'doc', winProp);
		if (!win) {
			exibirModalErro('Por favor, permita pop-ups para visualizar o documento.');
			return;
		}
		var t = frm.target;
		var a = frm.action;
		frm.target = 'doc';
		frm.action = pdf ? 'preverPdf' : 'prever';
		frm.submit();
		frm.target = t;
		frm.action = a;
		win.focus();
	}

	// ===== MODELOS =====
	function getListaModelos() {
		this.carregando = true;
		if (typeof sigaSpinner !== 'undefined' && sigaSpinner.mostrar) sigaSpinner.mostrar();
		$('.selected-label').append('<span id="select-spinner" class="spinner-border text-secondary" role="status"></span><span class="disabled"> Carregando...</span>');
		const idModEl = document.getElementsByName('exDocumentoDTO.idMod')[0];
		const idMod = idModEl ? idModEl.value : '';
		const isEditandoAnexo = document.getElementsByName('exDocumentoDTO.criandoAnexo')[0] ? document.getElementsByName('exDocumentoDTO.criandoAnexo')[0].value === "true" : false;
		const isCriandoSubprocesso = document.getElementsByName('exDocumentoDTO.criandoSubprocesso')[0] ? document.getElementsByName('exDocumentoDTO.criandoSubprocesso')[0].value === "true" : false;
		const isAutuando = document.getElementsByName('exDocumentoDTO.autuando')[0] ? document.getElementsByName('exDocumentoDTO.autuando')[0].value === "true" : false;
		const siglaMobPaiEl = document.getElementsByName('exDocumentoDTO.mobilPaiSel.sigla')[0];
		const siglaMobPai = siglaMobPaiEl ? siglaMobPaiEl.value : '';
		
		var qry = (isEditandoAnexo ? 'isEditandoAnexo=true&' : '')
				+ (isCriandoSubprocesso ? 'isCriandoSubprocesso=true&' : '')
				+ (isAutuando ? 'isAutuando=true&' : '')
				+ (siglaMobPai != undefined && siglaMobPai != "" ? 'siglaMobPai=' + siglaMobPai : '');
		
		var ulMod = $('#ulmod');

		$.ajax({
			url : "/sigaex/api/v1/modelos/lista-hierarquica?" + qry,
			contentType : "application/json",
			dataType : 'json',
			success : function(result) {
				if (result && result.list && result.list.length > 0) {
					setUserSessionStorage('lastQry', qry);
					setUserSessionStorage('modelos', JSON.stringify(result.list));
					carregaModelos(ulMod, result.list);
				}
			},
			error : function() {
				if (typeof sigaSpinner !== 'undefined' && sigaSpinner.ocultar) sigaSpinner.ocultar();
			}
		});
	}

	function carregaModelos(ulMod, listMod) {
		for (var i = 0; i < listMod.length; i++) {
			var item = listMod[i];
			var liMod = "<li class='dropdown-item' data-value='" + item.idModelo
					+ "' data-level='" + item.level + "' data-search='" + item.descr + "' "
					+ (item.group ? 'data-group ' : '')
					+ (item.idModelo == '${exDocumentoDTO.idMod}' ? 'data-default-selected ' : '') + ">";
			if (item.group) {
				liMod = liMod + "<a href='#'>" + item.nome + "</a></li>";
			} else {
				liMod = liMod + "<a href='#' class='d-inline'>" + item.nome
						+ "<small class='pl-2 text-muted'>" + (item.keywords != undefined ? item.keywords : '') + "</small></a></li>";
			}
			ulMod.append(liMod);
		}
		if (typeof sigaSpinner !== 'undefined' && sigaSpinner.ocultar) sigaSpinner.ocultar();
		$('#modelos-select').hierarchySelect({
			width : 'auto',
			height : 'auto'
		});
	}

	function alterouOrigem() {
		<c:if test="${exDocumentoDTO.doc.codigo == 'NOVO' and exDocumentoDTO.tipoDocumento == 'interno'}">
		if (typeof retorna_subscritor === 'function') retorna_subscritor('', '', '', '');
		</c:if>
		document.getElementById('alterouModelo').value = 'true';
	}

	function alterouModeloSelect() {
		var valor = $('input[name="exDocumentoDTO.idMod"]').val();
		var valorOriginal = $('input[name="exDocumentoDTO.idMod.original"]').val();
		if (valor !== '' && valor !== valorOriginal) {
			document.getElementById('alterouModelo').value = 'true';
			sbmt();
		}
	}

	$(document).ready(function() {
		getListaModelos();
		personalizacaoSeparar();
		
		var campoData = document.getElementById('dataAtual');
		if (campoData && !campoData.value) {
			var hoje = new Date();
			var dd = String(hoje.getDate()).padStart(2, '0');
			var mm = String(hoje.getMonth() + 1).padStart(2, '0');
			var yyyy = hoje.getFullYear();
			campoData.value = dd + '/' + mm + '/' + yyyy;
		}
		
		$('[data-toggle="tooltip"]').tooltip();

		// Garante que o modal do SIGA exista
		if (typeof sigaModal === 'undefined') {
			console.warn('sigaModal não encontrado, usando fallback Bootstrap.');
		}
	});

	window.onbeforeunload = function() {
		if (typeof sigaSpinner !== 'undefined' && sigaSpinner.mostrar) sigaSpinner.mostrar();
	};
</script>

<script type="text/javascript" src="/siga/javascript/select2/select2.min.js"></script>
<script type="text/javascript" src="/siga/javascript/select2/i18n/pt-BR.js"></script>
<script type="text/javascript" src="/siga/javascript/siga.select2.js"></script>
