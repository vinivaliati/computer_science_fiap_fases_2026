# Estruturas estáticas da colônia: hierarquia de sistemas,
# prioridades e limiares de decisão.

SISTEMAS_COLONIA = {
    'sistema_energetico': {
        'paineis_solares': {'quantidade': 120, 'area_m2': 500, 'eficiencia_pct': 22},
        'baterias':        {'capacidade_kwh': 200, 'tipo': 'ion-litio'},
    },
    'sistema_habitacional': {
        'modulos':      ['modulo_alpha', 'modulo_beta', 'modulo_gama'],
        'suporte_vida': True,
        'pressao_bar':  1.0,
    },
    'sistema_comunicacao': {
        'antena_principal': True,
        'antena_backup':    True,
        'delay_terra_min':  20,
    },
    'sistema_cientifico': {
        'laboratorio':      True,
        'sensores_externos': 8,
    },
}

# 1 = maior prioridade (nunca desligar), 4 = menor
PRIORIDADE_SISTEMAS = {
    'suporte_vida': 1,
    'comunicacao':  2,
    'laboratorio':  3,
    'navegacao':    4,
}

LIMIARES = {
    'bateria_critica':   20,   # % — emergência
    'bateria_baixa':     40,   # % — alerta
    'consumo_alto':      65,   # kWh
    'geracao_baixa':     35,   # kWh
    'temp_min':          18,   # °C
    'temp_max':          28,   # °C
    'excedente_kwh':     15,   # kWh acima do consumo → armazenar
    'deficit_kwh':       10,   # kWh abaixo da geração → risco
}