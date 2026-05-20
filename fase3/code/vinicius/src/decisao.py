from src.dados import PRIORIDADE_SISTEMAS

# limiares de decisao
LIMIAR_BATERIA_CRITICO  = 20   # %
LIMIAR_BATERIA_BAIXO    = 40   # %
LIMIAR_CONSUMO_ALTO     = 65   # kWh
LIMIAR_GERACAO_BAIXA    = 35   # kWh
LIMIAR_TEMP_INTERNA_MIN = 18   # °C
LIMIAR_TEMP_INTERNA_MAX = 28   # °C


def avaliar_nivel_energia(reserva_pct):
    if reserva_pct < LIMIAR_BATERIA_CRITICO:
        return 'critico'
    elif reserva_pct < LIMIAR_BATERIA_BAIXO:
        return 'baixo'
    else:
        return 'normal'


def avaliar_consumo(energia_consumida_kwh):
    if energia_consumida_kwh > LIMIAR_CONSUMO_ALTO:
        return 'alto'
    return 'normal'


def decidir_acao(estado):
    reserva      = estado['reserva_bateria_pct']
    consumo      = estado['energia_consumida_kwh']
    gerada       = estado['energia_gerada_kwh']
    temp_interna = estado['temp_interna_c']

    nivel_energia = avaliar_nivel_energia(reserva)
    nivel_consumo = avaliar_consumo(consumo)

    acoes = []

    # regra 1: bateria critica — modo emergencia
    if nivel_energia == 'critico':
        acoes.append("EMERGENCIA: bateria critica. Desligar sistemas nao essenciais imediatamente.")
        sistemas_desligar = [s for s, p in PRIORIDADE_SISTEMAS.items() if p > 1]
        acoes.append(f"  Sistemas a desligar (por prioridade): {', '.join(sistemas_desligar)}")

    # regra 2: bateria baixa E consumo alto — modo economia
    elif nivel_energia == 'baixo' and nivel_consumo == 'alto':
        acoes.append("ALERTA: bateria baixa e consumo alto. Ativar modo economia.")
        acoes.append("  Reduzir operacao de: laboratorio, navegacao.")

    # regra 3: bateria baixa, consumo normal — monitorar
    elif nivel_energia == 'baixo':
        acoes.append("AVISO: reserva de bateria abaixo de 40%. Monitorar consumo.")

    # regra 4: geracao baixa — verificar paineis
    if gerada < LIMIAR_GERACAO_BAIXA:
        acoes.append("AVISO: geracao solar abaixo do esperado. Verificar paineis.")

    # regra 5: temperatura interna fora da faixa segura
    if temp_interna < LIMIAR_TEMP_INTERNA_MIN:
        acoes.append(f"ALERTA: temperatura interna {temp_interna}°C abaixo do minimo ({LIMIAR_TEMP_INTERNA_MIN}°C). Ativar aquecimento.")
    elif temp_interna > LIMIAR_TEMP_INTERNA_MAX:
        acoes.append(f"ALERTA: temperatura interna {temp_interna}°C acima do maximo ({LIMIAR_TEMP_INTERNA_MAX}°C). Ativar resfriamento.")

    # tudo normal
    if not acoes:
        acoes.append("STATUS: sistemas operando dentro dos parametros normais.")

    return acoes


def exibir_decisao(acoes):
    print("\n--- DECISOES DO SISTEMA ---")
    for acao in acoes:
        print(f"  {acao}")