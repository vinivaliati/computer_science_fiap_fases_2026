def regressao_linear(x, y):
    """
    Ajusta y = a*x + b (mínimos quadrados, sem bibliotecas) e retorna (a, b).
    """
    n = len(x)
    if n < 2 or n != len(y):
        raise ValueError("Listas x e y devem ter mesmo tamanho e n >= 2.")

    sx = sum(x)
    sy = sum(y)
    sx2 = sum(v * v for v in x)
    sxy = sum(x[i] * y[i] for i in range(n))

    denom = n * sx2 - sx * sx
    if denom == 0:
        raise ValueError("Não é possível ajustar reta (denominador zero).")

    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return a, b


def prever_y(a, b, x_novo):
    return a * x_novo + b
