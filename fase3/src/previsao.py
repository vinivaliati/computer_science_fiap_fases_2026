# Regressão linear simples por mínimos quadrados.
# Relaciona irradiância solar (W/m²) com energia gerada (kWh).


def calcular_regressao(registros):
    x = [r['irradiancia_solar'] for r in registros]
    y = [r['energia_gerada']    for r in registros]
    n = len(x)

    media_x = sum(x) / n
    media_y = sum(y) / n

    numerador   = sum((x[i] - media_x) * (y[i] - media_y) for i in range(n))
    denominador = sum((x[i] - media_x) ** 2               for i in range(n))

    a = numerador / denominador       # coeficiente angular
    b = media_y - a * media_x         # intercepto

    return round(a, 4), round(b, 4)


def prever(irradiancia, a, b):
    return round(a * irradiancia + b, 2)