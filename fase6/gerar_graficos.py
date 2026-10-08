# gerar_graficos.py
# Script auxiliar: le dados_aurora_siger.csv e gera o grafico de apoio
# salvo em graficos_ou_imagens/analise_latencia_status.png.
# Nao faz parte do menu principal do sistema (codigo_fonte.py).

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("dados_aurora_siger.csv")

os.makedirs("graficos_ou_imagens", exist_ok=True)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))

# latencia prevista x latencia real, com a linha de previsao perfeita como referencia
axs[0].scatter(df["latencia_prevista_ms"], df["latencia_real_ms"], alpha=0.7, color="#3b6ea5")
limite = max(df["latencia_prevista_ms"].max(), df["latencia_real_ms"].max()) + 10
axs[0].plot([0, limite], [0, limite], linestyle="--", color="gray", label="Previsao perfeita")
axs[0].set_xlabel("Latencia prevista (ms)")
axs[0].set_ylabel("Latencia real (ms)")
axs[0].set_title("Latencia prevista vs. real")
axs[0].legend()

# distribuicao de alertas por status
cores = {"Normal": "#4caf50", "Atencao": "#ff9800", "Critico": "#e53935"}
contagem = df["status"].value_counts().reindex(["Normal", "Atencao", "Critico"]).fillna(0)
axs[1].bar(contagem.index, contagem.values, color=[cores[s] for s in contagem.index])
axs[1].set_title("Distribuicao de alertas por status")
axs[1].set_ylabel("Quantidade de registros")

plt.tight_layout()
plt.savefig("graficos_ou_imagens/analise_latencia_status.png", dpi=130)
print("Grafico salvo em graficos_ou_imagens/analise_latencia_status.png")
