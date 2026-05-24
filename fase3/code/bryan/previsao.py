#  Bryan Lima Garcia
#  previsao.py — Previsão por regressão linear simples
# -
#  Responsabilidade: ajustar uma reta y = a*x + b a partir de
#  dados históricos e usá-la para estimar valores futuros.
# -
#  Exemplo de uso:
#    vento  = [8, 10, 12]   → variável independente (x)
#    eolica = [20, 25, 30]  → variável dependente   (y)
#    a, b = regressao_linear(vento, eolica)
#    prever_y(a, b, x_novo=11)  →  ≈ 27.5 kW
# -


def regressao_linear(x, y):
    """
    Calcula os coeficientes a e b da reta y = a*x + b
    pelo método dos mínimos quadrados (sem bibliotecas externas).

    Parâmetros
    ----------
    x : list[float] — variável independente (ex.: velocidade do vento)
    y : list[float] — variável dependente   (ex.: energia gerada)

    Retorno
    -------
    (a, b) : tupla com inclinação e intercepto da reta
    """
    n = len(x)

    if n < 2 or n != len(y):
        raise ValueError("As listas x e y devem ter tamanho igual e n >= 2.")

    soma_x   = sum(x)
    soma_y   = sum(y)
    soma_x2  = sum(v * v for v in x)
    soma_xy  = sum(x[i] * y[i] for i in range(n))

    denominador = n * soma_x2 - soma_x * soma_x

    if denominador == 0:
        raise ValueError("Não é possível ajustar a reta: denominador é zero.")

    a = (n * soma_xy - soma_x * soma_y) / denominador
    b = (soma_y - a * soma_x) / n

    return a, b


def prever_y(a, b, x_novo):
    """
    Aplica a equação y = a*x + b para estimar um valor futuro.

    Parâmetros
    ----------
    a, b   : coeficientes obtidos de regressao_linear()
    x_novo : novo valor de entrada (ex.: vento previsto)

    Retorno
    -------
    float — valor estimado de y
    """
    return a * x_novo + b
