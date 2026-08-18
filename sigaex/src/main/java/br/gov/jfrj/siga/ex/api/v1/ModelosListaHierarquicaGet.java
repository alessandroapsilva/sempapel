package br.gov.jfrj.siga.ex.api.v1;

import java.util.ArrayList;
import java.util.List;

import br.gov.jfrj.siga.dp.DpLotacao;
import br.gov.jfrj.siga.dp.DpPessoa;
import br.gov.jfrj.siga.ex.ExMobil;
import br.gov.jfrj.siga.ex.ExModelo;
import br.gov.jfrj.siga.ex.api.v1.IExApiV1.IModelosListaHierarquicaGet;
import br.gov.jfrj.siga.ex.api.v1.IExApiV1.ModeloListaHierarquicaItem;
import br.gov.jfrj.siga.ex.bl.Ex;
import br.gov.jfrj.siga.hibernate.ExDao;
import br.gov.jfrj.siga.util.ListaHierarquica;
import br.gov.jfrj.siga.util.ListaHierarquicaItem;

public class ModelosListaHierarquicaGet implements IModelosListaHierarquicaGet {

	private static final String MODELO_CERTIDAO_DESENTRANHAMENTO = "Certidão de desentranhamento";

	@Override
	public String getContext() {
		return "obter lista de modelos";
	}

	@Override
	public void run(Request req, Response resp, ExApiV1Context ctx) throws Exception {
		boolean isEditandoAnexo = (req.isEditandoAnexo != null && req.isEditandoAnexo ? true : false);
		boolean isCriandoSubprocesso = (req.isCriandoSubprocesso != null && req.isCriandoSubprocesso ? true : false);
		ExMobil mobPai = null;
		String headerValue = null;
		boolean isAutuando = (req.isAutuando != null && req.isAutuando ? true : false);

		if (req.siglaMobPai != null) {
			mobPai = ctx.buscarMobil(req.siglaMobPai, req, resp, "Documento Pai");
		}
		DpPessoa titular = ctx.getTitular();
		DpLotacao lotaTitular = ctx.getLotaTitular();
		List<ExModelo> modelos = Ex.getInstance().getBL().obterListaModelos(null, null, isEditandoAnexo,
				isCriandoSubprocesso, mobPai, headerValue, true, titular, lotaTitular, isAutuando);

		/*
		 * A Certidão de desentranhamento é um modelo de sistema e, por isso,
		 * normalmente é filtrada da lista de criação. Para o fluxo específico de
		 * "Incluir documento" ela precisa estar disponível para criação como peça
		 * filha do documento atual.
		 */
		if (isEditandoAnexo) {
			ExModelo certidao = ExDao.getInstance().consultarExModelo(null, MODELO_CERTIDAO_DESENTRANHAMENTO);
			if (certidao != null && !contemModelo(modelos, certidao)) {
				modelos.add(certidao.getModeloAtual());
			}
		}

		resp.list = new ArrayList<>();
		for (ListaHierarquicaItem m : getListaHierarquica(modelos).getList()) {
			ModeloListaHierarquicaItem mi = new ModeloListaHierarquicaItem();
			mi.idModelo = (m.getValue() != null ? m.getValue().toString() : "");
			mi.idModeloInicial = (m.getIdInicial() != null ? m.getIdInicial().toString() : "");
			mi.nome = m.getText();
			mi.descr = m.getSearchText();
			mi.level = (long) m.getLevel();
			mi.group = m.getGroup();
			mi.selected = m.getSelected();
			mi.keywords = m.getKeywords();
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

	private ListaHierarquica getListaHierarquica(List<ExModelo> modelos) {
		ListaHierarquica lh = new ListaHierarquica();
		for (ExModelo m : modelos) {
			lh.add(m.getIdInicial().toString(), m.getNmMod(), m.getDescMod(), m.getId(), false);
		}
		return lh;
	}
}
