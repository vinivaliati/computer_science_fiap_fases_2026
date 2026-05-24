#  Bryan Lima Garcia
#  decisao.py — Regras de decisão automática da colônia
# -
#  Responsabilidade: transformar dados em uma ação clara,
#  usando regras de prioridade simples e bem definidas.
# -
#  Prioridade das regras (da mais crítica para a normal):
#    1. Temperatura extrema - proteger climatização
#    2. Energia crítica - cortar cargas não essenciais
#    3. Energia baixa + consumo alto - modo economia
#    4. Energia baixa - monitorar e reduzir
#    5. Situação normal - operação padrão
# -


def decidir_acao(colonia):
    """
    Analisa os dados da colônia e retorna uma decisão em texto.

    Parâmetros
    ----------
    colonia : dict  — dicionário criado por criar_colonia()

    Retorno
    -------
    str — mensagem de ação (ex.: "ALERTA: reduzir consumo")
    """
    d = colonia["dados"]

    energia_pct = d["energia_reserva_pct"]
    consumo_kw  = d["consumo_total_kw"]
    temp_c      = d["clima"]["temperatura_c"]

    geracao_kw  = d["geracao_solar_kw"] + d["geracao_eolica_kw"]

    # Consumo alto = consumo >= 85 % da geração (ou geração = 0)
    consumo_alto = (geracao_kw == 0 and consumo_kw > 0) or \
                   (consumo_kw >= 0.85 * geracao_kw)

    # Temperatura extrema = abaixo de -20 °C ou acima de 35 °C
    temp_extrema = temp_c <= -20 or temp_c >= 35

    # ─ Regra 1: temperatura extrema
    if temp_extrema:
        return (
            f"ATENÇÃO: temperatura extrema ({temp_c} °C). "
            "Priorizar energia para climatização e manter SEGURANÇA ativa."
        )

    # ─ Regra 2: energia crítica (< 25 %)
    if energia_pct < 25:
        return (
            "CRÍTICO: Energia < 25 % - Manter SEGURANÇA ativa. "
            "Ativar modo economia e cortar cargas não essenciais."
        )

    # ─ Regra 3: energia baixa E consumo alto
    if energia_pct < 50 and consumo_alto:
        return (
            "ALERTA: energia < 50 % e consumo alto. "
            "Ativar modo economia e reduzir consumo."
        )

    # ─ Regra 4: energia baixa (sem consumo alto)
    if energia_pct < 50:
        return "ALERTA: Energia baixa - Reduzir consumo e monitorar geração."

    # ─ Regra 5: operação normal
    return "OK: Operação normal - Segurança ativa."
