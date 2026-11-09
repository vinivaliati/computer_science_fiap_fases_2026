"""
modelo.py - modelagem linear (etapa 5): análise exploratória, regressão simples e múltipla.

  Simples:   consumo total da colônia  ~  ciclo   (tendência -> previsão dos próximos ciclos)
  Múltipla:  consumo_kwh do módulo     ~  tipo + ciclo + temperatura + ocupação
"""
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import dados

PASTA_GRAFICOS = os.path.join(dados.PASTA, "graficos_ou_imagens")


def carregar():
    conexao = sqlite3.connect(dados.CAMINHO_BANCO)
    try:
        return pd.read_sql_query("SELECT * FROM registros", conexao)
    finally:
        conexao.close()


def analise_exploratoria(df):
    print("\n  === Análise exploratória ===")
    print("  Registros:", len(df))
    print(df[["consumo_kwh", "bateria_pct", "temperatura_c", "ocupacao_pct"]]
          .describe().loc[["mean", "std", "min", "max"]].round(1).to_string())
    print("\n  Correlação com o consumo (Pearson):")
    corr = df[["consumo_kwh", "ciclo", "temperatura_c", "ocupacao_pct", "bateria_pct"]].corr()
    print(corr["consumo_kwh"].drop("consumo_kwh").round(2).to_string())


def ajustar_tendencia(df):
    """Ajusta consumo total ~ ciclo. Devolve (modelo, tabela por ciclo)."""
    por_ciclo = df.groupby("ciclo")["consumo_kwh"].sum().reset_index()
    modelo = LinearRegression().fit(por_ciclo[["ciclo"]], por_ciclo["consumo_kwh"])
    return modelo, por_ciclo


def regressao_simples(df):
    """Consumo total por ciclo ~ ciclo."""
    modelo, por_ciclo = ajustar_tendencia(df)
    y = por_ciclo["consumo_kwh"]
    r2 = r2_score(y, modelo.predict(X))
    print("\n  === Regressão linear simples: consumo total ~ ciclo ===")
    print("  consumo = %.1f + %.2f * ciclo   (R² = %.2f)" % (modelo.intercept_, modelo.coef_[0], r2))
    print("  Interpretação: a cada ciclo o consumo total sobe cerca de %.1f kWh." % modelo.coef_[0])
    for c in (7, 8):
        print("  Previsão ciclo %d: %.1f kWh" % (c, modelo.predict(pd.DataFrame({"ciclo": [c]}))[0]))
    plt.figure(figsize=(7, 4))
    plt.scatter(por_ciclo["ciclo"], y, label="Observado")
    eixo = pd.DataFrame({"ciclo": range(1, 9)})
    plt.plot(eixo["ciclo"], modelo.predict(eixo), color="orange", label="Reta de regressão")
    plt.title("Consumo total da colônia por ciclo")
    plt.xlabel("Ciclo")
    plt.ylabel("Consumo (kWh)")
    plt.grid(alpha=0.3)
    plt.legend()
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    plt.savefig(os.path.join(PASTA_GRAFICOS, "regressao_simples.png"), dpi=120, bbox_inches="tight")
    plt.close()
    print("  Gráfico salvo em graficos_ou_imagens/regressao_simples.png")
    return modelo


def regressao_multipla(df):
    """Consumo do módulo ~ tipo (one-hot) + ciclo + temperatura + ocupação."""
    X = pd.get_dummies(df[["tipo", "ciclo", "temperatura_c", "ocupacao_pct"]], columns=["tipo"],
                       drop_first=True).astype(float)
    y = df["consumo_kwh"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42)
    modelo = LinearRegression().fit(X_tr, y_tr)
    prev = modelo.predict(X_te)
    media = np.full(len(y_te), y_tr.mean())   # baseline: chutar sempre a média
    print("\n  === Regressão linear múltipla (treino %d / teste %d) ===" % (len(X_tr), len(X_te)))
    print("  %-22s MAE %6.2f | RMSE %6.2f | R² %5.2f" % (
        "Modelo", mean_absolute_error(y_te, prev), np.sqrt(mean_squared_error(y_te, prev)),
        r2_score(y_te, prev)))
    print("  %-22s MAE %6.2f | RMSE %6.2f | R² %5.2f" % (
        "Baseline (média)", mean_absolute_error(y_te, media),
        np.sqrt(mean_squared_error(y_te, media)), r2_score(y_te, media)))
    print("\n  Coeficientes (efeito no consumo, mantendo os demais fixos):")
    for nome, coef in sorted(zip(X.columns, modelo.coef_), key=lambda p: -abs(p[1])):
        print("   %-24s %+8.2f" % (nome, coef))
    print("  Intercepto: %.2f" % modelo.intercept_)
    print("  (tipo é comparado com 'agricultura', a categoria de referência.)")
    return modelo


def menu_modelo():
    try:
        df = carregar()
        if len(df) < 20:
            print("  Poucos registros no banco para treinar o modelo.")
            return
        analise_exploratoria(df)
        regressao_simples(df)
        regressao_multipla(df)
    except (sqlite3.Error, ValueError) as erro:
        print("  Erro ao executar o modelo:", erro)


if __name__ == "__main__":
    dados.preparar()
    menu_modelo()
