# gerar_dados.py
# Script usado APENAS para gerar o arquivo dados_aurora_siger.csv a partir de
# dados simulados (sensores fictícios da colônia Aurora Siger em Marte).
# Não faz parte do menu principal do sistema, mas mostra como os dados
# simulados foram construídos (reprodutibilidade garantida pelo seed fixo).


import numpy as np
import pandas as pd

# Seed fixo -> os mesmos dados são gerados sempre que o script rodar novamente
np.random.seed(42)

# Módulos operacionais da colônia (serão usados também na busca por prefixo - Trie)
modulos = [
    "Comunicacao Principal",
    "Comunicacao Secundaria",
    "Controle de Navegacao",
    "Controle Ambiental",
    "Suporte Vital",
    "Suporte Energetico",
    "Sensoriamento Externo",
    "Sensoriamento Interno",
    "Hidroponia",
    "Seguranca Perimetral",
]

status_possiveis = ["Normal", "Atencao", "Critico"]
risco_possivel = ["Baixo", "Medio", "Alto"]

n_registros = 60
linhas = []

for i in range(n_registros):
    modulo = np.random.choice(modulos)

    # Latência prevista (modelo/baseline) e latência real observada (ms)
    latencia_prevista = np.round(np.random.uniform(10, 120), 2)
    # ruído realista: a latência real varia em torno da prevista
    ruido = np.random.normal(0, 8)
    latencia_real = max(1.0, np.round(latencia_prevista + ruido, 2))

    # Eletricidade básica aplicada à comunicação (tensão/corrente dos módulos)
    tensao_v = np.round(np.random.uniform(3.3, 12.0), 2)   # volts
    corrente_a = np.round(np.random.uniform(0.1, 2.5), 3)  # ampères

    # Código do sensor em hexadecimal (ex: 0x1A, 0x2F...) -> bases numéricas
    codigo_sensor_dec = np.random.randint(0, 255)
    codigo_sensor_hex = f"0x{codigo_sensor_dec:02X}"

    # Criticidade de 1 (baixa) a 5 (altíssima) -> usada na fila de prioridade (heap)
    criticidade = int(np.random.randint(1, 6))

    # Tempo desde o registro do alerta (minutos) -> também pondera prioridade
    tempo_desde_registro = int(np.random.randint(0, 180))

    # Status derivado de forma simples a partir da criticidade + atraso de latência
    atraso = latencia_real - latencia_prevista
    if criticidade >= 4 or atraso > 15:
        status = "Critico"
    elif criticidade == 3 or atraso > 5:
        status = "Atencao"
    else:
        status = "Normal"

    risco_operacional = np.random.choice(
        risco_possivel, p=[0.5, 0.35, 0.15] if status == "Normal" else [0.2, 0.4, 0.4]
    )

    linhas.append({
        "id_alerta": f"AL-{i+1:03d}",
        "modulo": modulo,
        "codigo_sensor_hex": codigo_sensor_hex,
        "codigo_sensor_dec": codigo_sensor_dec,
        "status": status,
        "criticidade": criticidade,
        "latencia_prevista_ms": latencia_prevista,
        "latencia_real_ms": latencia_real,
        "tensao_v": tensao_v,
        "corrente_a": corrente_a,
        "tempo_desde_registro_min": tempo_desde_registro,
        "risco_operacional": risco_operacional,
    })

df = pd.DataFrame(linhas)
df.to_csv("dados_aurora_siger.csv", index=False, encoding="utf-8")

print("Arquivo 'dados_aurora_siger.csv' gerado com sucesso!")
print(df.head())
print(f"\nTotal de registros: {len(df)}")
