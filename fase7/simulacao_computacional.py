"""
simulacao_computacional.py - simulação do estado de carga (SoC) da bateria da colônia (etapa 5).

Ideia: em cada ciclo (1 sol = 24 h) a colônia gera energia só durante o dia e consome o dia todo.
O estado de carga é a INTEGRAL do saldo de potência ao longo do tempo:

    SoC(t) = SoC0 + (1/CAPACIDADE) * integral de 0 até t de [ g(s) - c(s) ] ds

  g(t) = P_max * sen(pi*(t-6)/12)   para 6h <= t <= 18h, senão 0   (painéis solares)
  c(t) = consumo médio do ciclo (kWh/24h) com leve variação diária (mais uso à noite)

A integral é calculada numericamente (regra do trapézio) e conferida com a fórmula exata.
Os dados de cada ciclo vêm do banco (soma do consumo e geração real do ciclo).
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulos"))

import matplotlib
matplotlib.use("Agg")          
import matplotlib.pyplot as plt
import numpy as np

import dados

PASTA_GRAFICOS = os.path.join(dados.PASTA, "graficos_ou_imagens")
CAPACIDADE_KWH = 300.0          # capacidade do banco de baterias
SOC_INICIAL = 60.0              # % no início do ciclo
HORAS = 24
PASSO = 0.05                    # h 


def integral(y, t):
    """Regra do trapézio: soma a área de cada fatia (base = passo, alturas = dois valores vizinhos)."""
    return float(np.sum((y[1:] + y[:-1]) / 2 * np.diff(t)))


def totais_do_ciclo(ciclo):
    """Soma consumo e geração (kWh) de todos os módulos no ciclo, direto do banco."""
    conexao = sqlite3.connect(dados.CAMINHO_BANCO)
    try:
        return conexao.execute(
            "SELECT SUM(consumo_kwh), SUM(geracao_kwh) FROM registros WHERE ciclo = ?",
            (ciclo,)).fetchone()
    finally:
        conexao.close()


def potencia_geracao(t, energia_dia):
    """g(t): meia senoide entre 6h e 18h. P_max sai de: integral de g = energia do dia.
    Integral exata de P*sen(pi*(t-6)/12) em [6,18] = P*24/pi  ->  P = energia*pi/24."""
    p_max = energia_dia * np.pi / 24.0
    return np.where((t >= 6) & (t <= 18), p_max * np.sin(np.pi * (t - 6) / 12.0), 0.0)


def potencia_consumo(t, energia_dia):
    """c(t): média + variação suave (consumo ~15% maior à noite, quando há aquecimento)."""
    media = energia_dia / HORAS
    return media * (1 + 0.15 * np.cos(2 * np.pi * (t - 24) / HORAS))


def simular(ciclo, fator_geracao=1.0):
    """Roda a simulação de um ciclo. fator_geracao < 1 simula tempestade de poeira."""
    consumo_total, geracao_total = totais_do_ciclo(ciclo)
    if consumo_total is None:
        raise ValueError("Ciclo %s não tem registros no banco." % ciclo)
    geracao_total *= fator_geracao

    t = np.arange(0, HORAS + PASSO, PASSO)
    saldo = potencia_geracao(t, geracao_total) - potencia_consumo(t, consumo_total)  # kW

    # integral acumulada pelo método do trapézio: área de cada fatia entre dois instantes
    energia_acum = np.concatenate(([0.0], np.cumsum((saldo[1:] + saldo[:-1]) / 2 * PASSO)))
    soc = np.clip(SOC_INICIAL + 100 * energia_acum / CAPACIDADE_KWH, 0, 100)

    return {
        "t": t, "soc": soc, "saldo": saldo,
        "gerado": float(integral(potencia_geracao(t, geracao_total), t)),
        "consumido": float(integral(potencia_consumo(t, consumo_total), t)),
        "geracao_media_kw": float(integral(potencia_geracao(t, geracao_total), t) / HORAS),
        "soc_final": float(soc[-1]), "soc_min": float(soc.min()),
        "horas_criticas": float((soc < 20).sum() * PASSO),
        "geracao_exata": geracao_total,   # valor teórico da integral, para conferir o erro
    }


def ciclo_mais_critico():
    """Ciclo do banco com o menor SoC final em operação normal (usado pelo menu 9 e pelos agentes)."""
    conexao = sqlite3.connect(dados.CAMINHO_BANCO)
    try:
        ciclos = [l[0] for l in conexao.execute("SELECT DISTINCT ciclo FROM registros")]
    finally:
        conexao.close()
    if not ciclos:
        raise ValueError("O banco está vazio.")
    return min(ciclos, key=lambda c: simular(c)["soc_final"])


def exibir(ciclo):
    cenarios = [("Normal", 1.0), ("Tempestade de poeira (geração 40%)", 0.4)]
    plt.figure(figsize=(9, 4.5))
    print("\n  Simulação do ciclo %d (capacidade %.0f kWh, SoC inicial %.0f%%)" % (
        ciclo, CAPACIDADE_KWH, SOC_INICIAL))
    for nome, fator in cenarios:
        r = simular(ciclo, fator)
        erro = abs(r["gerado"] - r["geracao_exata"])
        print("\n  Cenário: %s" % nome)
        print("    Energia gerada (integral numérica): %.1f kWh (exata %.1f, erro %.3f)" % (
            r["gerado"], r["geracao_exata"], erro))
        print("    Energia consumida: %.1f kWh | geração média: %.1f kW" % (
            r["consumido"], r["geracao_media_kw"]))
        print("    SoC final: %.1f%% | SoC mínimo: %.1f%% | horas abaixo de 20%%: %.1f h" % (
            r["soc_final"], r["soc_min"], r["horas_criticas"]))
        plt.plot(r["t"], r["soc"], label=nome)
    plt.axhline(20, color="red", linestyle="--", linewidth=1, label="Limite crítico (20%)")
    plt.title("Estado de carga da bateria - ciclo %d" % ciclo)
    plt.xlabel("Hora do sol marciano (h)")
    plt.ylabel("Estado de carga (%)")
    plt.ylim(0, 100)
    plt.grid(alpha=0.3)
    plt.legend()
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    arquivo = os.path.join(PASTA_GRAFICOS, "simulacao_soc_ciclo%d.png" % ciclo)
    plt.savefig(arquivo, dpi=120, bbox_inches="tight")
    plt.close()
    print("\n  Gráfico salvo em graficos_ou_imagens/simulacao_soc_ciclo%d.png" % ciclo)


def menu_simulacao():
    try:
        ciclo = int(input("  Ciclo para simular (1 a 6, sugestão 4): ").strip() or "4")
        exibir(ciclo)
    except ValueError as erro:
        print("  Entrada inválida:", erro)


if __name__ == "__main__":
    dados.preparar()
    for c in (1, 4):
        exibir(c)
