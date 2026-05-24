#  Bryan Lima Garcia
#  analise.py — Análise do balanço energético da colônia
# -
#  Responsabilidade: comparar geração e consumo e gerar uma
#  recomendação clara sobre o estado energético atual.
#  -
#  Situações verificadas:
#    consumo > geração - déficit (alerta ou crítico)
#    geração > consumo - excedente (sugestão de armazenamento)
#    geração = consumo - equilíbrio
# -


def analisar_energia(geracao_kw, consumo_kw, reserva_pct):
    """
    Compara geração e consumo e retorna uma mensagem de análise.

    Parâmetros
    ----------
    geracao_kw  : float — energia gerada no momento (solar + eólica)
    consumo_kw  : float — energia consumida pela colônia
    reserva_pct : float — nível da bateria de reserva (0-100 %)

    Retorno
    -------
    str — diagnóstico energético com recomendação de ação
    """

    # ─ Déficit: consumo supera a geração
    if consumo_kw > geracao_kw:
        deficit = consumo_kw - geracao_kw

        if reserva_pct < 25:
            return (
                f"CRÍTICO: consumo > geração (déficit = {deficit:.1f} kW) "
                f"e reserva em {reserva_pct} % - Cortar carga imediatamente."
            )

        return (
            f"ALERTA: consumo > geração (déficit = {deficit:.1f} kW). "
            "Usar reserva e reduzir consumo."
        )

    # ─ Excedente: geração supera o consumo
    if geracao_kw > consumo_kw:
        excedente = geracao_kw - consumo_kw

        if reserva_pct < 95:
            return (
                f"SUGESTÃO: armazenar energia excedente "
                f"(excedente = {excedente:.1f} kW)."
            )

        return (
            f"OK: excedente = {excedente:.1f} kW — "
            "bateria praticamente cheia."
        )

    # ─ Equilíbrio
    return "OK: geração e consumo em equilíbrio."
