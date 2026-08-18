package br.gov.jfrj.siga.ex.api.v1;

import java.util.ArrayList;
import java.util.List;

import br.gov.jfrj.siga.ex.ExMobil;
import br.gov.jfrj.siga.ex.ExModelo;
import br.gov.jfrj.siga.ex.api.v1.IExApiV1.IDocumentosSiglaModelosParaIncluirGet;
import br.gov.jfrj.siga.ex.api.v1.IExApiV1.ModeloItem;
import br.gov.jfrj.siga.ex.bl.Ex;
import br.gov.jfrj.siga.hibernate.ExDao;

public class DocumentosSiglaModelosParaIncluirGet implements IDocumentosSiglaModelosParaIncluirGet {

	private static final String MODELO_CERTIDAO_DESENTRANHAMENTO = "Certidão de desentranhamento";

	@Override
	public String getContext() {
		return "obter lista de modelos";
	}

	@Override
	public void run(Request req, Response resp, ExApiV1Context ctx) throws Exception {
		boolean isEditandoAnexo = true;
		boolean isCriandoSubprocesso = false;
		String headerValue = null;
		boolean isAutuando = false;

		ExMobil mobPai = ctx.buscarEValidarMobil(req.sigla, req, resp, "Documento Principal");

		List<ExModelo> modelos = Ex.getInstance().getBL().obterListaModelos(null, null, isEditandoAnexo,
				isCriandoSubprocesso, mobPai, headerValue, true, ctx.getTitular(), ctx.getLotaTitular(), isAutuando);

		/*
		 * Este modelo é marcado pelo SIGA como modelo de sistema e fica fora da
		 * lista comum de criação. No fluxo de inclusão de documento ele precisa
		 * aparecer para que a certidão possa ser criada como documento filho.
		 */
		ExModelo certidao = ExDao.getInstance().consultarExModelo(null, MODELO_CERTIDAO_DESENTRANHAMENTO);
		if (certidao != null && !contemModelo(modelos, certidao)) {
			modelos.add(certidao.getModeloAtual());
		}

		resp.list = new ArrayList<>();
		for (ExModelo m : modelos) {
			ModeloItem mi = new ModeloItem();
			mi.idModelo = m.getId().toString();
			mi.idModeloInicial = m.getIdInicial().toString();
			mi.nome = m.getNmMod();
			mi.descr = m.getDescMod();
			resp.list.add(mi);
		}
	}

	private boolean contemModelo(List<ExModelo> modelos, ExModelo modelo) {
		Long idInicial = modelo.getIdInicial();
		for (ExModelo item : modelos) {
			if (item != null && item.getIdInicial() != null && item.getIdInicial().equals(idInicial)) {
				return true;
			}
		}
		return false;
	}

}
