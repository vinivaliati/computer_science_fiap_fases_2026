from src.dados import LIMIARES


def analisar_balanco(registro):
    gerada   = registro['energia_gerada']
    consumida = registro['energia_consumida']
    reserva  = registro['reserva_bateria']
    balanco  = round(gerada - consumida, 2)

    if balanco < -LIMIARES['deficit_kwh']:
        status      = 'DEFICIT'
        mensagem    = f"ALERTA: consumo maior que geracao por {abs(balanco)} kWh. Usar reserva ou reduzir consumo."
    elif balanco > LIMIARES['excedente_kwh']:
        status      = 'EXCEDENTE'
        mensagem    = f"SUGESTAO: excedente de {balanco} kWh. Armazenar energia nas baterias."
    else:
        status      = 'EQUILIBRADO'
        mensagem    = f"Balanco estavel ({balanco:+.2f} kWh). Manter operacao."

    return {
        'gerada':    gerada,
        'consumida': consumida,
        'balanco':   balanco,
        'reserva':   reserva,
        'status':    status,
        'mensagem':  mensagem,
    }