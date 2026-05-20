import random

random.seed(42)

N_DIAS = 365


def _valor_com_anomalia(min_val, max_val, chance_anomalia=0.12):
    # chance_anomalia: probabilidade de gerar um valor fora da faixa normal
    if random.random() < chance_anomalia:
        amplitude = max_val - min_val
        if random.random() < 0.5:
            return round(random.uniform(min_val - amplitude * 0.5, min_val - 0.1), 2)
        else:
            return round(random.uniform(max_val + 0.1, max_val + amplitude * 0.5), 2)
    return round(random.uniform(min_val, max_val), 2)


def _clamp(valor, minimo, maximo):
    if minimo is not None and valor < minimo:
        return minimo
    if maximo is not None and valor > maximo:
        return maximo
    return valor


def gerar_dados():
    registros = []

    for dia in range(1, N_DIAS + 1):
        irradiancia      = _clamp(_valor_com_anomalia(400, 700), 0, 1000)
        energia_gerada   = _clamp(round(irradiancia * 0.10 + random.gauss(0, 3), 2), 0, None)
        energia_consumida = _clamp(_valor_com_anomalia(40, 75), 0, None)
        reserva_bateria  = _clamp(_valor_com_anomalia(20, 100), 0, 100)
        temp_interna     = _valor_com_anomalia(18, 26)
        temp_externa     = _valor_com_anomalia(-80, -10)

        registros.append({
            'dia':               dia,
            'irradiancia_solar': irradiancia,
            'energia_gerada':    energia_gerada,
            'energia_consumida': energia_consumida,
            'reserva_bateria':   reserva_bateria,
            'temp_interna':      temp_interna,
            'temp_externa':      temp_externa,
        })

    random.shuffle(registros)
    return registros