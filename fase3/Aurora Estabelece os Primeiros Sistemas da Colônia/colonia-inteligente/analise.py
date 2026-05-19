def analisar_energia(geracao_total_kw, consumo_total_kw, energia_reserva_pct):
    if consumo_total_kw > geracao_total_kw:
        deficit = consumo_total_kw - geracao_total_kw

        if energia_reserva_pct < 25:
            return (
                f"CRÍTICO: consumo > geração (déficit = {deficit} kW) "
                f"e reserva crítica ({energia_reserva_pct}%). Cortar carga imediatamente."
            )

        return f"ALERTA: consumo > geração (déficit = {deficit} kW). Usar reserva e reduzir consumo."

    if geracao_total_kw > consumo_total_kw:
        excedente = geracao_total_kw - consumo_total_kw
        if energia_reserva_pct < 95:
            return f"SUGESTÃO: armazenar energia excedente (excedente = {excedente} kW)."
        return f"OK: excedente = {excedente} kW, bateria praticamente cheia."

    return "OK: geração e consumo em equilíbrio."
