from colonia import criar_colonia, listar_subsistemas
from previsao import regressao_linear, prever_y
from decisao import decidir_acao
from analise import analisar_energia

def calcular_geracao_total(dados):
    return dados["geracao_solar_kw"] + dados["geracao_eolica_kw"]

def simular_cenario(cenario, desc, ids_hist):
    print("\n" + "="*60)
    print(f"[{desc}]")
    print("-" * 60)
    print("Entradas:")
    print(f"energia_reserva_pct =", cenario['dados']['energia_reserva_pct'])
    print(f"consumo_total_kw    =", cenario['dados']['consumo_total_kw'])
    print(f"geracao_solar_kw    =", cenario['dados']['geracao_solar_kw'])
    print(f"geracao_eolica_kw   =", cenario['dados']['geracao_eolica_kw'])
    print(f"vento_mps           =", cenario['dados']['clima']['vento_mps'])
    print(f"temperatura_c       =", cenario['dados']['clima']['temperatura_c'])

    # Decisão automática
    decisao = decidir_acao(cenario)

    # Previsão (regressão - vento -> energia eólica)
    hist_vento = cenario['historico'][ids_hist[0]]
    hist_eolica = cenario['historico'][ids_hist[1]]
    a_e, b_e = regressao_linear(hist_vento, hist_eolica)
    vento_atual = cenario["dados"]["clima"]["vento_mps"]
    prev_eolica_kw = prever_y(a_e, b_e, vento_atual)

    # Análise de energia final
    geracao_total_kw = calcular_geracao_total(cenario["dados"])
    analise = analisar_energia(geracao_total_kw, cenario["dados"]["consumo_total_kw"], cenario["dados"]["energia_reserva_pct"])

    print("\nSaídas:")
    print("Decisão automática:")
    print(decisao)
    print("\nPrevisão (regressão linear):")
    print(f"Eólica: energia_eolica = {a_e:.2f}*vento + {b_e:.2f} → previsão ≈ {prev_eolica_kw:.2f} kW")
    print("\nAnálise de energia:")
    print(analise)
    print("="*60)

def executar():
    print("=== SISTEMA COLÔNIA INTELIGENTE ===")
    print("Energia | Clima | Segurança | Temperatura")
    
    # Histórico padrão (para todos os exemplos serem coerentes)
    ids_hist = ("vento_mps", "energia_eolica_kw")
    historico = {
        "vento_mps": [8, 10, 12],
        "energia_eolica_kw": [20, 25, 30]
    }

    # Exemplo 1 — Normal (sem alerta)
    ex1 = {
        "dados": {
            "energia_reserva_pct": 55,
            "consumo_total_kw": 40,
            "geracao_solar_kw": 30,
            "geracao_eolica_kw": 25,
            "clima": {
                "vento_mps": 11,
                "temperatura_c": -10
            }
        },
        "sistemas": criar_colonia()["sistemas"],
        "historico": historico
    }
    
    # Exemplo 2 — Energia baixa + consumo alto
    ex2 = {
        "dados": {
            "energia_reserva_pct": 40,
            "consumo_total_kw": 28,
            "geracao_solar_kw": 20,
            "geracao_eolica_kw": 10,
            "clima": {
                "vento_mps": 10,
                "temperatura_c": 5
            }
        },
        "sistemas": criar_colonia()["sistemas"],
        "historico": historico
    }
    
    # Exemplo 3 — Temperatura extrema + déficit
    ex3 = {
        "dados": {
            "energia_reserva_pct": 60,
            "consumo_total_kw": 35,
            "geracao_solar_kw": 10,
            "geracao_eolica_kw": 15,
            "clima": {
                "vento_mps": 12,
                "temperatura_c": -25
            }
        },
        "sistemas": criar_colonia()["sistemas"],
        "historico": historico
    }

    simular_cenario(ex1, "EXEMPLO 1 — Situação normal", ids_hist)
    simular_cenario(ex2, "EXEMPLO 2 — Energia baixa + consumo alto", ids_hist)
    simular_cenario(ex3, "EXEMPLO 3 — Temperatura extrema + déficit", ids_hist)

if __name__ == "__main__":
    executar()
