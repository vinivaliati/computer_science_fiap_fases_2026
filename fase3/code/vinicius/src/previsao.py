import math


# regressao linear simples (minimos quadrados)
# relaciona irradiancia solar (W/m²) com energia gerada (kWh)


def calcular_regressao(irradiancia_lista, energia_lista):
    n = len(irradiancia_lista)
    if n != len(energia_lista) or n < 2:
        raise ValueError("Listas devem ter o mesmo tamanho e ao menos 2 pontos.")

    soma_x  = sum(irradiancia_lista)
    soma_y  = sum(energia_lista)
    soma_xy = sum(irradiancia_lista[i] * energia_lista[i] for i in range(n))
    soma_x2 = sum(x ** 2 for x in irradiancia_lista)

    # coeficiente angular (a) e intercepto (b) da reta y = a*x + b
    denominador = n * soma_x2 - soma_x ** 2
    if denominador == 0:
        raise ValueError("Dados insuficientes para ajuste linear (variancia zero).")

    a = (n * soma_xy - soma_x * soma_y) / denominador
    b = (soma_y - a * soma_x) / n

    return a, b


def prever_energia(irradiancia, a, b):
    return round(a * irradiancia + b, 2)


def calcular_r2(irradiancia_lista, energia_lista, a, b):
    n = len(irradiancia_lista)
    media_y = sum(energia_lista) / n
    ss_tot = sum((y - media_y) ** 2 for y in energia_lista)
    ss_res = sum((energia_lista[i] - (a * irradiancia_lista[i] + b)) ** 2 for i in range(n))
    if ss_tot == 0:
        return 1.0
    return round(1 - ss_res / ss_tot, 4)


def exibir_modelo(a, b, r2):
    print("\n--- MODELO DE PREVISAO (Regressao Linear) ---")
    print(f"  Equacao : energia = {round(a, 4)} * irradiancia + {round(b, 4)}")
    print(f"  R²      : {r2}  (quanto o modelo explica a variacao)")


def exibir_previsao(irradiancia, energia_prevista):
    print(f"\n--- PREVISAO ---")
    print(f"  Irradiancia entrada : {irradiancia} W/m²")
    print(f"  Energia estimada    : {energia_prevista} kWh")