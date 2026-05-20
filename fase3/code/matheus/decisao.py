def decidir_acao(colonia):
    d = colonia["dados"]

    energia_pct = d["energia_reserva_pct"]
    consumo_kw = d["consumo_total_kw"]
    temp_c = d["clima"]["temperatura_c"]

    geracao_kw = d["geracao_solar_kw"] + d["geracao_eolica_kw"]
    # Evita divisão/limiar estranho quando geração = 0
    consumo_alto = (geracao_kw == 0 and consumo_kw > 0) or (consumo_kw >= 0.85 * geracao_kw)

    temp_extrema = (temp_c <= -20) or (temp_c >= 35)

    # 1) Temperatura extrema tem prioridade operacional (sem desligar segurança)
    if temp_extrema:
        return (
            f"ATENÇÃO: temperatura extrema ({temp_c}°C). "
            "Priorizar energia para climatização e manter SEGURANÇA ativa."
        )

    # 2) Energia crítica
    if energia_pct < 25:
        return (
            "CRÍTICO: energia < 25%. Manter SEGURANÇA ativa. "
            "Ativar modo economia e cortar cargas não essenciais."
        )

    # 3) Energia baixa + consumo alto
    if energia_pct < 50 and consumo_alto:
        return (
            "ALERTA: energia < 50% e consumo alto (próximo/maior que a geração). "
            "Ativar modo economia e reduzir consumo."
        )

    # 4) Energia baixa (geral)
    if energia_pct < 50:
        return "ALERTA: energia baixa. Reduzir consumo e monitorar geração."

    # 5) Normal
    return "OK: operação normal (segurança ativa)."
