# Organiza os dados da colonia em estruturas adequadas:
# - dicionario para estado atual
# - hierarquia de sistemas
# - historico em listas


ESTADO_INICIAL = {
    'irradiancia_solar':     500.0,
    'energia_gerada_kwh':    50.0,
    'energia_consumida_kwh': 60.0,
    'reserva_bateria_pct':   45.0,
    'temp_interna_c':        22.0,
    'temp_externa_c':        -55.0,
}

# hierarquia de sistemas da colonia
SISTEMAS_COLONIA = {
    'sistema_energetico': {
        'paineis_solares': {
            'quantidade': 120,
            'area_m2': 500,
            'eficiencia_pct': 22,
        },
        'baterias': {
            'capacidade_kwh': 200,
            'tipo': 'ion-litio',
        },
    },
    'sistema_habitacional': {
        'modulos': ['modulo_alpha', 'modulo_beta', 'modulo_gama'],
        'suporte_vida': True,
        'pressao_bar': 1.0,
    },
    'sistema_comunicacao': {
        'antena_principal': True,
        'antena_backup': True,
        'delay_terra_min': 20,
    },
    'sistema_cientifico': {
        'laboratorio': True,
        'sensores_externos': 8,
    },
}

# prioridade dos sistemas (1 = maior prioridade)
PRIORIDADE_SISTEMAS = {
    'suporte_vida':  1,
    'comunicacao':   2,
    'laboratorio':   3,
    'navegacao':     4,
}


def criar_estado(irradiancia, energia_gerada, energia_consumida, reserva_bateria,
                 temp_interna, temp_externa):
    return {
        'irradiancia_solar':     irradiancia,
        'energia_gerada_kwh':    energia_gerada,
        'energia_consumida_kwh': energia_consumida,
        'reserva_bateria_pct':   reserva_bateria,
        'temp_interna_c':        temp_interna,
        'temp_externa_c':        temp_externa,
    }


def exibir_estado(estado):
    print("\n--- ESTADO DA COLONIA ---")
    print(f"  Irradiancia solar    : {estado['irradiancia_solar']} W/m²")
    print(f"  Energia gerada       : {estado['energia_gerada_kwh']} kWh")
    print(f"  Energia consumida    : {estado['energia_consumida_kwh']} kWh")
    print(f"  Reserva bateria      : {estado['reserva_bateria_pct']}%")
    print(f"  Temp interna         : {estado['temp_interna_c']}°C")
    print(f"  Temp externa         : {estado['temp_externa_c']}°C")


def exibir_hierarquia(sistemas=None, nivel=0):
    if sistemas is None:
        sistemas = SISTEMAS_COLONIA
    for chave, valor in sistemas.items():
        print("  " * nivel + f"[{chave}]")
        if isinstance(valor, dict):
            exibir_hierarquia(valor, nivel + 1)
        else:
            print("  " * (nivel + 1) + str(valor))