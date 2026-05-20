from src.dados     import criar_estado, exibir_estado, exibir_hierarquia
from src.decisao   import decidir_acao, exibir_decisao
from src.previsao  import calcular_regressao, prever_energia, calcular_r2, exibir_modelo, exibir_previsao
from src.energia   import analisar_balanco, exibir_balanco


# dados historicos para treinar o modelo de regressao
# irradiancia (W/m²) e energia gerada (kWh) medidos nos ultimos dias
HISTORICO_IRRADIANCIA = [380, 420, 450, 470, 500, 510, 530, 560, 590, 620, 640, 670, 700]
HISTORICO_ENERGIA     = [ 42,  44,  48,  50,  52,  54,  56,  58,  62,  65,  67,  70,  72]


def main():
    print("=" * 55)
    print("   SISTEMA DE GESTAO - COLONIA ESPACIAL MARTE-I")
    print("=" * 55)

    # --- estado atual da colonia ---
    estado = criar_estado(
        irradiancia=480,
        energia_gerada=40,
        energia_consumida=70,
        reserva_bateria=35,
        temp_interna=22,
        temp_externa=-58,
    )
    exibir_estado(estado)

    # --- hierarquia de sistemas ---
    print("\n--- HIERARQUIA DE SISTEMAS ---")
    exibir_hierarquia()

    # --- analise energetica ---
    balanco = analisar_balanco(
        estado['energia_gerada_kwh'],
        estado['energia_consumida_kwh'],
        estado['reserva_bateria_pct'],
    )
    exibir_balanco(balanco)

    # --- decisoes automaticas ---
    acoes = decidir_acao(estado)
    exibir_decisao(acoes)

    # --- modelo de previsao ---
    a, b = calcular_regressao(HISTORICO_IRRADIANCIA, HISTORICO_ENERGIA)
    r2   = calcular_r2(HISTORICO_IRRADIANCIA, HISTORICO_ENERGIA, a, b)
    exibir_modelo(a, b, r2)

    irradiancia_futura = 550
    energia_prevista   = prever_energia(irradiancia_futura, a, b)
    exibir_previsao(irradiancia_futura, energia_prevista)

    print("\n" + "=" * 55)


if __name__ == '__main__':
    main()