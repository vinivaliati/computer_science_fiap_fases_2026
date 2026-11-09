"""
analise.py - "Analisar sustentabilidade da colônia": junta banco, regra booleana, estrutura de
dados, simulação e regressão em uma única análise com recomendação e limitações (etapa 8).
"""
import heapq

import pandas as pd

import dados
import regras
import estruturas
import simulacao_computacional as sim
import modelo


def analise_final():
    registros = dados.consultar()
    if not registros:
        print("  O banco está vazio. Cadastre registros ou recarregue o CSV.")
        return
    print("\n====== ANÁLISE DE SUSTENTABILIDADE DA COLÔNIA ======")

    # 1) Banco + regra booleana
    resultado = regras.analisar_registros()
    riscos = [(r, x) for r, x in resultado if x["risco"]]
    alertas = [(r, x) for r, x in resultado if x["alerta"] and not x["risco"]]
    print("\n1) Registros no banco: %d | em RISCO: %d | em ALERTA: %d" % (
        len(registros), len(riscos), len(alertas)))

    # 2) Estrutura de dados: fila de prioridade
    print("\n2) Fila de prioridade (3 mais urgentes):")
    fila = estruturas.montar_fila_alertas()
    for _ in range(min(3, len(fila))):
        prio, ciclo, id_reg, modulo, msg = heapq.heappop(fila)
        print("   prioridade %d | %s | ciclo %d | %s" % (-prio, modulo, -ciclo, msg))

    # 3) Simulação do pior ciclo (menor saldo de energia)
    pior = sim.ciclo_mais_critico()
    normal, tempestade = sim.simular(pior), sim.simular(pior, 0.4)
    print("\n3) Simulação do ciclo mais crítico (%d): SoC final %.1f%% em operação normal e "
          "%.1f%% (mín. %.1f%%) em tempestade de poeira." % (
              pior, normal["soc_final"], tempestade["soc_final"], tempestade["soc_min"]))

    # 4) Modelo linear: tendência do consumo
    df = modelo.carregar()
    reg, _ = modelo.ajustar_tendencia(df)
    prox = int(df["ciclo"].max()) + 1
    previsto = float(reg.predict(pd.DataFrame({"ciclo": [prox]}))[0])
    geracao_media = df.groupby("ciclo")["geracao_kwh"].sum().mean()
    print("\n4) Tendência: consumo total sobe %.1f kWh por ciclo; previsão do ciclo %d = %.1f kWh "
          "(geração média atual: %.1f kWh)." % (reg.coef_[0], prox, previsto, geracao_media))

    # 5) Recomendação
    print("\n5) RECOMENDAÇÃO TÉCNICA (sugestão, precisa de decisão humana):")
    if previsto > geracao_media:
        print("   - O consumo previsto passa a geração média: ampliar a geração/armazenamento ou "
              "reduzir cargas não essenciais antes do ciclo %d." % prox)
    else:
        print("   - Geração média cobre o consumo previsto, mas sem folga para tempestades.")
    for r, x in riscos:
        print("   - Inspecionar %s no ciclo %d (risco pela regra booleana)." % (
            r["codigo_modulo"], r["ciclo"]))
    if tempestade["soc_min"] < 20:
        print("   - Em tempestade de poeira a bateria fica abaixo de 20%: preparar modo econômico "
              "protegendo suporte à vida e habitação.")

    # 6) Limitações
    print("\n6) LIMITAÇÕES:")
    print("   - Base simulada (48 registros, 6 ciclos): serve para demonstrar o método, não para")
    print("     prever Marte de verdade. Capacidade da bateria e limites são hipóteses.")
    print("   - O R² alto da regressão múltipla vem sobretudo do tipo do módulo; a tendência por")
    print("     ciclo usa só 6 pontos. Os agentes de IA precisam de internet e chave; as respostas")
    print("     do modelo podem variar e passam por aprovação humana.")
