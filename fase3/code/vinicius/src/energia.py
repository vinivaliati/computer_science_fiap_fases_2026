LIMIAR_EXCEDENTE_KWH = 15   # kWh — excedente vale armazenar
LIMIAR_DEFICIT_KWH   = 10   # kWh — deficit exige atencao


def analisar_balanco(energia_gerada, energia_consumida, reserva_bateria_pct):
    balanco = round(energia_gerada - energia_consumida, 2)
    resultado = {
        'energia_gerada':      energia_gerada,
        'energia_consumida':   energia_consumida,
        'balanco_kwh':         balanco,
        'reserva_bateria_pct': reserva_bateria_pct,
        'status':              '',
        'recomendacao':        '',
    }

    if balanco < -LIMIAR_DEFICIT_KWH:
        resultado['status'] = 'DEFICIT'
        resultado['recomendacao'] = (
            f"ALERTA: consumo maior que geracao por {abs(balanco)} kWh. "
            "Reduzir sistemas nao essenciais ou usar reserva de bateria."
        )
    elif balanco > LIMIAR_EXCEDENTE_KWH:
        resultado['status'] = 'EXCEDENTE'
        resultado['recomendacao'] = (
            f"SUGESTAO: excedente de {balanco} kWh disponivel. "
            "Armazenar energia nas baterias."
        )
    else:
        resultado['status'] = 'EQUILIBRADO'
        resultado['recomendacao'] = (
            f"Balanco energetico estavel ({balanco:+.2f} kWh). "
            "Manter operacao atual."
        )

    return resultado


def exibir_balanco(resultado):
    print("\n--- ANALISE ENERGETICA ---")
    print(f"  Gerado       : {resultado['energia_gerada']} kWh")
    print(f"  Consumido    : {resultado['energia_consumida']} kWh")
    print(f"  Balanco      : {resultado['balanco_kwh']:+.2f} kWh  [{resultado['status']}]")
    print(f"  Bateria      : {resultado['reserva_bateria_pct']}%")
    print(f"  {resultado['recomendacao']}")