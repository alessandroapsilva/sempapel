/*******************************************************************************
 * Copyright (c) 2006 - 2011 SJRJ.
 * 
 *     This file is part of SIGA.
 * 
 *     SIGA is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 * 
 *     SIGA is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 * 
 *     You should have received a copy of the GNU General Public License
 *     along with SIGA.  If not, see <http://www.gnu.org/licenses/>.
 ******************************************************************************/
package br.gov.jfrj.siga.ex;

import java.io.IOException;
import java.util.Date;
import java.util.Map;
import java.util.Set;

import javax.persistence.Column;
import javax.persistence.MappedSuperclass;

import br.gov.jfrj.itextpdf.Documento;
import br.gov.jfrj.itextpdf.Stamp;
import br.gov.jfrj.siga.base.Prop;
import br.gov.jfrj.siga.dp.DpLotacao;
import br.gov.jfrj.siga.dp.DpPessoa;
import br.gov.jfrj.siga.model.Objeto;
@MappedSuperclass
public abstract class ExArquivo extends Objeto {
	@Column(name = "NUM_PAGINAS")
	private Integer numPaginas;

	public abstract String getAssinantesCompleto();
	
	public String getVinculosCompleto() {
		return "";
	}

	public abstract Set<ExMovimentacao> getAssinaturasDigitais();

	/**
	 * Retorna o número de páginas de um arquivo.
	 * 
	 * @return Número de páginas de um arquivo.
	 * 
	 */
	public Integer getContarNumeroDePaginas() {
		try {
			byte[] abPdf = null;
			abPdf = getPdf();
			if (abPdf == null)
				return null;
			return Documento.getNumberOfPages(abPdf);
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Retorna o pdf do documento com stamp. Método criado para tentar stampar
	 * um documento que está sendo anexado.
	 * 
	 * @return pdf com stamp.
	 * 
	 */
	public byte[] getArquivoComStamp() {
		try {
			byte[] abPdf = null;
			abPdf = getPdf();
			if (abPdf == null)
				return null;

			// Verifica se é possível estampar o documento
			try {
				byte[] documentoComStamp = Stamp.stamp(abPdf, "", true,
						false, false, false, false, null, null, null, null, null,
						null, null, "", null);

				return documentoComStamp;

			} catch (Exception e) {
				return null;
			}
		} catch (Exception e) {
			return null;
		}
	}

	/**
	 * Retorna o número de bytes no PDF.
	 * 
	 * @return número de bytes no PDF.
	 * 
	 */
	public int getNumBytes() {
		try {
			byte[] abPdf = null;
			abPdf = getPdf();
			if (abPdf == null)
				return 0;
			return abPdf.length;
		} catch (Exception e) {
			return 0;
		}
	}
	
	//public abstract Date getData();

	public abstract String getHtml();

	public abstract String getHtmlComReferencias() throws Exception;

	public Long getIdDoc() {
		if (this instanceof ExDocumento) {
			ExDocumento doc = (ExDocumento) this;
			return doc.getIdDoc();
		}
		;

		if (this instanceof ExMovimentacao) {
			ExMovimentacao mov = (ExMovimentacao) this;
			return mov.getIdMov();
		}

		return null;
	}
	
	public Date getData() {
		if (this instanceof ExDocumento) {
			ExDocumento doc = (ExDocumento) this;
			return doc.getData();
		}
		;

		if (this instanceof ExMovimentacao) {
			ExMovimentacao mov = (ExMovimentacao) this;
			return mov.getData();
		}

		return null;
	}

	public abstract DpLotacao getLotacao();

	/**
	 * Complementa o carimbo com os dados funcionais do assinante.
	 * Mantém o texto principal de assinatura do SIGA e acrescenta somente
	 * identificação funcional, lotação e órgão quando disponíveis.
	 */
	private String getDetalhesFuncionaisAssinantes(boolean comLink) {
		Set<ExMovimentacao> assinaturas = getAssinaturasDigitais();
		if (assinaturas == null || assinaturas.isEmpty())
			return "";

		StringBuilder sb = new StringBuilder();
		for (ExMovimentacao mov : assinaturas) {
			if (mov == null)
				continue;

			DpPessoa pessoa = mov.getTitular() != null ? mov.getTitular() : mov.getCadastrante();
			if (pessoa == null)
				continue;

			DpLotacao lotacao = pessoa.getLotacao();
			String funcao = pessoa.getFuncaoString();
			String identificacao = pessoa.getSigla();

			StringBuilder detalhe = new StringBuilder();
			if (identificacao != null && !identificacao.trim().isEmpty())
				detalhe.append("Usuário: ").append(identificacao.trim());

			if (funcao != null && !funcao.trim().isEmpty()) {
				if (detalhe.length() > 0)
					detalhe.append(" - ");
				detalhe.append("Cargo/Função: ").append(funcao.trim());
			}

			if (lotacao != null) {
				if (detalhe.length() > 0)
					detalhe.append(" - ");
				detalhe.append("Lotação: ");
				if (lotacao.getNomeLotacao() != null && !lotacao.getNomeLotacao().trim().isEmpty())
					detalhe.append(lotacao.getNomeLotacao().trim());
				else
					detalhe.append(lotacao.getSigla());

				if (lotacao.getSiglaCompletaFormatada() != null && !lotacao.getSiglaCompletaFormatada().trim().isEmpty())
					detalhe.append(" (").append(lotacao.getSiglaCompletaFormatada().trim()).append(")");

				if (lotacao.getOrgaoUsuario() != null) {
					String orgao = lotacao.getOrgaoUsuario().getDescricao();
					if (orgao != null && !orgao.trim().isEmpty())
						detalhe.append(" - Órgão: ").append(orgao.trim());
				}
			}

			if (detalhe.length() > 0) {
				if (comLink)
					sb.append("<br/>");
				else
					sb.append("\n");
				sb.append(detalhe);
			}
		}

		if (sb.length() > 0) {
			if (comLink)
				sb.append("<br/>");
			else
				sb.append("\n");
		}
		return sb.toString();
	}

	/**
	 * Retorna uma mensagem informando quem assinou o documento e o endereço
	 * onde o usuário pode verificar a autenticidade de um documento com base em
	 * um código gerado.
	 * 
	 */
	public String getMensagem(boolean comLink) {
		String sMensagem = "";
		sMensagem += getVinculosCompleto();
		if (isAssinadoDigitalmente()) {
			
			sMensagem += getAssinantesCompleto();
			sMensagem += getDetalhesFuncionaisAssinantes(comLink);
			sMensagem += "Documento Nº: " + getSiglaAssinatura()
					+ " - consulta à autenticidade em ";
			
			if (comLink) 
				sMensagem += "<a href='"+ getQRCode() +"' target='_Blank'>" + getQRCode() + "</a>";
			else
				sMensagem += getQRCode();
			

		}
		return sMensagem;
	}
	
	public String getMensagem() {
		return getMensagem(false);
	}

	/**
	 * Caso o método esteja sendo executado em um objeto do tipo documento,
	 * retorna a código do documento. Caso o método esteja sendo executado em um
	 * objeto do tipo movimentação, retorna o nome do arquivo desta
	 * movimentação.
	 * 
	 */
	public String getNome() {
		if (this instanceof ExDocumento) {
			ExDocumento doc = (ExDocumento) this;
			return doc.getCodigo();
		}

		if (this instanceof ExMovimentacao) {
			ExMovimentacao mov = (ExMovimentacao) this;
			return mov.getNmArqMov();
		}
		return null;
	}

	/**
	 * Retorna o número de páginas do documento para exibir no dossiê.
	 * 
	 */
	public int getNumeroDePaginasParaInsercaoEmDossie() {
		if (this instanceof ExMovimentacao) {
			ExMovimentacao mov = (ExMovimentacao) this;
			if (mov.getNumPaginasOri() != null)
				return mov.getNumPaginasOri();
		}
		return getNumPaginas();
	}

	public Integer getNumPaginas() {
		return numPaginas;
	}

	public abstract byte[] getPdf();
	
	public abstract boolean isPdf();

	public long getByteCount() {
		byte[] ab = getPdf();
		if (ab == null)
			return 0;
		return ab.length;
	}

	// public byte[] getPdfToHash() throws Exception {
	// byte[] pdf = getPdf();
	// if (pdf == null)
	// return null;
	// return AssinaturaDigital.getHasheableRangeFromPDF(pdf);
	// }
	//
	// public String getPdfToHashB64() throws Exception {
	// return Base64.encode(getPdfToHash());
	// }

	public String getQRCode() {
		if (isAssinadoDigitalmente()) {
			String sQRCode;
			sQRCode = Prop.get("/sigaex.autenticidade.url") + "?n="
					+ getSiglaAssinatura();
			return sQRCode;
		}
		return null;
	}

	/**
	 * Quando o objeto for do tipo documento retorna o código compacto do
	 * documento. Quando o objeto for do tipo movimentação retorna a referência
	 * da movimentação que é o codigo compacto da movimentação mais o id da
	 * movimentação.
	 * 
	 */
	public String getReferencia() {
		if (this instanceof ExDocumento) {
			ExDocumento doc = (ExDocumento) this;
			return doc.getCodigoCompacto();
		}

		if (this instanceof ExMovimentacao) {
			ExMovimentacao mov = (ExMovimentacao) this;
			return mov.getReferencia();
		}
		return null;
	}

	/**
	 * Retorna a referência do objeto mais o extensão ".html".
	 * 
	 */
	public String getReferenciaHtml() {
		if (getHtml() == null)
			return null;
		return getReferencia() + ".html";
	}

	/**
	 * Retorna a referência do objeto mais o extensão ".html" e um outro parâmetro de queryString para indicar o arquivo completo.
	 * 
	 */
	public String getReferenciaHtmlCompleto() {
		return getReferencia() + ".html&completo=1";
	}

	/**
	 * Retorna a referência do objeto mais o extensão ".pdf".
	 * 
	 */
	public String getReferenciaPDF() {
		if (getNumPaginas() == null || getNumPaginas() == 0)
			return null;
		return getReferencia() + ".pdf";
	};
	
	public String getReferenciaPDFCompleto() {
		if (getNumPaginas() == null || getNumPaginas() == 0)
			return null;
		return getReferencia() + ".pdf&completo=1";
	};
	
	/**
	 * Retorna a referência do objeto mais o extensão ".pdf".
	 * 
	 */
	public String getReferenciaZIP() {
		return getReferencia() + ".zip";
	};

	public Map<String, String> getResumo() {
		return null;
	};

	public abstract String getSiglaAssinatura();
	
	public abstract String getSiglaAssinaturaExterna();

	/**
	 * Verifica se um arquivo foi assinado digitalmente.
	 * 
	 * @return Verdadeiro caso o arquivo tenha sido assinado digitalmente e
	 *         Falso caso o arquivo não tenha sido assinado digitalmente.
	 * 
	 */
	public boolean isAssinadoDigitalmente() {
		return (getAssinaturasDigitais() != null)
				&& (getAssinaturasDigitais().size() > 0);
	}

	public abstract boolean isCancelado();

	public abstract boolean isRascunho();

	public abstract boolean isSemEfeito();

	public abstract boolean isInternoProduzido();

	public void setNumPaginas(Integer numPaginas) {
		this.numPaginas = numPaginas;
	}
	
	public abstract boolean isCodigoParaAssinaturaExterna(String num);
	
	public abstract String getTipoDescr();

}