import numpy as np
import pandas as pd
import os

N = 365  # um ano de leituras diarias
DISCREPANCIA_RANGE = [0.08, 0.15]

FAIXAS = {
    'irradiancia_solar':  (400, 700),   # W/m² (Marte recebe ~500 W/m² em media)
    'energia_gerada_kwh': (30, 80),     # kWh gerados pelos paineis
    'energia_consumida_kwh': (40, 75),  # kWh consumidos pela colonia
    'reserva_bateria_pct': (20, 100),   # % de carga da bateria
    'temp_interna_c':     (18, 26),     # °C dentro dos modulos habitaveis
    'temp_externa_c':     (-80, -10),   # °C superficie de Marte
}

SISTEMAS = ['suporte_vida', 'comunicacao', 'laboratorio', 'navegacao']


def gerar_valores(min_val, max_val, n, discrepancia):
    n_ok = int(n * (1 - discrepancia))
    n_bad = n - n_ok
    ok = np.random.uniform(min_val, max_val, n_ok)
    amplitude = max_val - min_val
    bad_baixo = np.random.uniform(min_val - amplitude * 0.5, min_val - 0.1, n_bad // 2)
    bad_alto  = np.random.uniform(max_val + 0.1, max_val + amplitude * 0.5, n_bad - n_bad // 2)
    return np.concatenate([ok, bad_baixo, bad_alto])


def gerar_dataset():
    np.random.seed(42)

    df = pd.DataFrame({'dia': range(1, N + 1)})

    for param, (min_val, max_val) in FAIXAS.items():
        disc = np.random.uniform(*DISCREPANCIA_RANGE)
        df[param] = gerar_valores(min_val, max_val, N, disc).round(2)

    # energia_gerada tem correlacao real com irradiancia (base para regressao)
    ruido = np.random.normal(0, 3, N)
    df['energia_gerada_kwh'] = (df['irradiancia_solar'] * 0.10 + ruido).round(2)

    for sistema in SISTEMAS:
        disc = np.random.uniform(*DISCREPANCIA_RANGE)
        df[sistema] = np.random.choice([1, 0], size=N, p=[1 - disc, disc])

    df = df.sample(frac=1).reset_index(drop=True)

    caminho = os.path.join(os.path.dirname(__file__), 'leituras_colonia.csv')
    df.to_csv(caminho, index=False)
    print(f"Dataset gerado: {len(df)} registros em '{caminho}'")
    return df


if __name__ == '__main__':
    gerar_dataset()