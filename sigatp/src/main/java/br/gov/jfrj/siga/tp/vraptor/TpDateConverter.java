package br.gov.jfrj.siga.tp.vraptor;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.enterprise.context.ApplicationScoped;

import br.com.caelum.vraptor.Convert;
import br.com.caelum.vraptor.converter.Converter;

/**
 * Conversor de datas exclusivo do SIGA-TP.
 *
 * Mantem a conversao dd/MM/yyyy utilizada pelo modulo legado sem repetir
 * br.gov.jfrj.siga.vraptor.DateConverter, que tambem existe no modulo VRaptor
 * atual e pode ser carregado no mesmo classloader no JBoss EAP.
 */
@Convert(Date.class)
@ApplicationScoped
public class TpDateConverter implements Converter<Date> {

    private static final String DATE_PATTERN = "dd/MM/yyyy";

    @Override
    public Date convert(String value, Class<? extends Date> type) {
        String normalized = stringOrNull(value);
        if (normalized == null) {
            return null;
        }

        try {
            SimpleDateFormat formatter = new SimpleDateFormat(DATE_PATTERN);
            formatter.setLenient(false);
            return formatter.parse(normalized);
        } catch (ParseException e) {
            return null;
        }
    }

    private static String stringOrNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.length() == 0 ? null : trimmed;
    }
}
