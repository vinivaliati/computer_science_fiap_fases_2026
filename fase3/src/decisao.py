from src.dados import LIMIARES, PRIORIDADE_SISTEMAS


def decidir(registro):
    reserva  = registro['reserva_bateria']
    consumo  = registro['energia_consumida']
    gerada   = registro['energia_gerada']
    temp     = registro['temp_interna']

    acoes = []

    if reserva < LIMIARES['bateria_critica']:
        descartaveis = [s for s, p in PRIORIDADE_SISTEMAS.items() if p > 1]
        acoes.append(f"EMERGENCIA: bateria critica ({reserva}%). Desligar: {', '.join(descartaveis)}.")

    elif reserva < LIMIARES['bateria_baixa'] and consumo > LIMIARES['consumo_alto']:
        acoes.append(f"ALERTA: bateria baixa ({reserva}%) e consumo alto ({consumo} kWh). Ativar modo economia.")
        acoes.append("  Reduzir operacao de: laboratorio, navegacao.")

    elif reserva < LIMIARES['bateria_baixa']:
        acoes.append(f"AVISO: reserva de bateria em {reserva}%. Monitorar consumo.")

    if gerada < LIMIARES['geracao_baixa']:
        acoes.append(f"AVISO: geracao solar baixa ({gerada} kWh). Verificar paineis.")

    if temp < LIMIARES['temp_min']:
        acoes.append(f"ALERTA: temperatura interna {temp}°C abaixo do minimo. Ativar aquecimento.")
    elif temp > LIMIARES['temp_max']:
        acoes.append(f"ALERTA: temperatura interna {temp}°C acima do maximo. Ativar resfriamento.")

    if not acoes:
        acoes.append("STATUS: sistemas operando normalmente.")

    return acoes


def classificar_status(acoes):
    texto = ' '.join(acoes)
    if 'EMERGENCIA' in texto:
        return 'EMERGENCIA'
    if 'ALERTA' in texto:
        return 'ALERTA'
    if 'AVISO' in texto:
        return 'AVISO'
    return 'NORMAL'