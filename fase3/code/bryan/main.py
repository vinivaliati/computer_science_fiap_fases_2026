#  Bryan Lima Garcia
#  main.py — Sistema de Gestão da Colônia Inteligente
# -
#  Ponto de entrada do sistema. Integra os módulos:
#    colonia  - estrutura e dados
#    decisao  - regras automáticas
#    previsao - regressão linear
#    analise  - balanço energético
#
#  Execute:  python main.py
# -

from colonia  import criar_colonia, listar_subsistemas
from decisao  import decidir_acao
from previsao import regressao_linear, prever_y
from analise  import analisar_energia


# ─ Helpers

def geracao_total(dados):
    """Soma a geração solar e eólica."""
    return dados["geracao_solar_kw"] + dados["geracao_eolica_kw"]


def separador(titulo=""):
    linha = "=" * 60
    if titulo:
        print(f"\n{linha}")
        print(f"  {titulo}")
        print(linha)
    else:
        print(linha)


# ─ Simulação de cenário

def simular_cenario(cenario, descricao):
    """
    Recebe um dicionário de cenário e imprime:
      - entradas (dados do momento)
      - decisão automática
      - previsão de geração eólica (regressão)
      - análise do balanço energético
    """
    d = cenario["dados"]
    separador(descricao)

    # Entradas
    print("\nEntradas:")
    print(f"  energia_reserva_pct : {d['energia_reserva_pct']} %")
    print(f"  consumo_total_kw    : {d['consumo_total_kw']} kW")
    print(f"  geracao_solar_kw    : {d['geracao_solar_kw']} kW")
    print(f"  geracao_eolica_kw   : {d['geracao_eolica_kw']} kW")
    print(f"  vento_mps           : {d['clima']['vento_mps']} m/s")
    print(f"  temperatura_c       : {d['clima']['temperatura_c']} °C")

    # ─ Decisão automática
    decisao = decidir_acao(cenario)

    # ─ Previsão por regressão linear
    hist_vento  = cenario["historico"]["vento_mps"]
    hist_eolica = cenario["historico"]["energia_eolica_kw"]
    a, b        = regressao_linear(hist_vento, hist_eolica)
    vento_atual = d["clima"]["vento_mps"]
    prev_eolica = prever_y(a, b, vento_atual)

    # ─ Análise de energia
    total_kw = geracao_total(d)
    analise  = analisar_energia(total_kw, d["consumo_total_kw"],
                                d["energia_reserva_pct"])

    # Saídas
    print("\nSaídas:")
    print(f"  [Decisão]   {decisao}")
    print(f"  [Previsão]  energia eólica ≈ {prev_eolica:.1f} kW "
          f"(para vento = {vento_atual} m/s | y = {a:.2f}x + {b:.2f})")
    print(f"  [Análise]   {analise}")


# ─ Ponto de entrada

def executar():
    print("\n" + "=" * 60)
    print("       SISTEMA DE GESTÃO — COLÔNIA INTELIGENTE")
    print("       Energia | Clima | Segurança | Previsão")
    print("=" * 60)

    # Histórico comum de regressão (vento → energia eólica)
    historico = {
        "vento_mps":         [8,  10, 12],
        "energia_eolica_kw": [20, 25, 30]
    }

    sistemas = criar_colonia()["sistemas"]

    # ─ Exemplo 1: operação normal
    cenario_1 = {
        "dados": {
            "energia_reserva_pct": 55,
            "consumo_total_kw":    40,
            "geracao_solar_kw":    30,
            "geracao_eolica_kw":   25,
            "clima": {"vento_mps": 11, "temperatura_c": -10}
        },
        "sistemas":  sistemas,
        "historico": historico
    }

    # ─ Exemplo 2: energia baixa + consumo alto
    cenario_2 = {
        "dados": {
            "energia_reserva_pct": 40,
            "consumo_total_kw":    28,
            "geracao_solar_kw":    20,
            "geracao_eolica_kw":   10,
            "clima": {"vento_mps": 10, "temperatura_c": 5}
        },
        "sistemas":  sistemas,
        "historico": historico
    }

    # ─ Exemplo 3: temperatura extrema + déficit
    cenario_3 = {
        "dados": {
            "energia_reserva_pct": 60,
            "consumo_total_kw":    35,
            "geracao_solar_kw":    10,
            "geracao_eolica_kw":   15,
            "clima": {"vento_mps": 12, "temperatura_c": -25}
        },
        "sistemas":  sistemas,
        "historico": historico
    }

    simular_cenario(cenario_1, "EXEMPLO 1 — Situação normal")
    simular_cenario(cenario_2, "EXEMPLO 2 — Energia baixa + consumo alto")
    simular_cenario(cenario_3, "EXEMPLO 3 — Temperatura extrema + déficit")

    # ─ Subsistemas detectados
    separador("SUBSISTEMAS DA COLÔNIA")
    colonia = criar_colonia()
    for caminho in listar_subsistemas(colonia):
        print(f"  {caminho}")

    print("\n" + "=" * 60)
    print("  Fim da simulação.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    executar()
