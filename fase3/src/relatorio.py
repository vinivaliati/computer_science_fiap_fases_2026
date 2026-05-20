from src.decisao import classificar_status


def _linha(char='=', n=55):
    print(char * n)


def imprimir_cabecalho():
    _linha()
    print("   SISTEMA DE GESTAO - COLONIA ESPACIAL MARTE")
    _linha()


def imprimir_hierarquia(sistemas, prefixo=''):
    itens = list(sistemas.items())
    for i, (chave, valor) in enumerate(itens):
        ultimo   = (i == len(itens) - 1)
        conector = '└── ' if ultimo else '├── '
        extensao = '    ' if ultimo else '│   '

        if isinstance(valor, dict):
            print(prefixo + conector + chave)
            imprimir_hierarquia(valor, prefixo + extensao)
        elif isinstance(valor, list):
            print(prefixo + conector + chave)
            for j, item in enumerate(valor):
                ult_item = (j == len(valor) - 1)
                print(prefixo + extensao + ('└── ' if ult_item else '├── ') + str(item))
        else:
            print(prefixo + conector + f"{chave}: {valor}")


def imprimir_resumo(processados):
    total = len(processados)

    contagem_balanco = {'DEFICIT': 0, 'EXCEDENTE': 0, 'EQUILIBRADO': 0}
    contagem_status  = {'EMERGENCIA': 0, 'ALERTA': 0, 'AVISO': 0, 'NORMAL': 0}

    for p in processados:
        contagem_balanco[p['balanco']['status']] += 1
        contagem_status[classificar_status(p['acoes'])] += 1

    print("\n--- RESUMO DOS 365 DIAS ---")
    print(f"  {'Total de registros':<22}: {total}")

    print(f"\n  Balanco energetico:")
    for status, qtd in contagem_balanco.items():
        pct = 100 * qtd // total
        print(f"    {status:<12}: {qtd:>3} dias ({pct}%)")

    print(f"\n  Status das decisoes:")
    for status, qtd in contagem_status.items():
        print(f"    {status:<12}: {qtd:>3} dias")


def imprimir_detalhe(processado, a, b, irradiancia_futura=550):
    from src.previsao import prever

    r   = processado['registro']
    bal = processado['balanco']

    _linha()
    print(f"   DIA {r['dia']} (selecionado aleatoriamente)")
    _linha()

    print("\n  ESTADO")
    print(f"    Irradiancia solar  : {r['irradiancia_solar']} W/m²")
    print(f"    Energia gerada     : {r['energia_gerada']} kWh")
    print(f"    Energia consumida  : {r['energia_consumida']} kWh")
    print(f"    Reserva bateria    : {r['reserva_bateria']}%")
    print(f"    Temp interna       : {r['temp_interna']}°C")
    print(f"    Temp externa       : {r['temp_externa']}°C")

    print(f"\n  ANALISE ENERGETICA")
    print(f"    Gerado             : {bal['gerada']} kWh")
    print(f"    Consumido          : {bal['consumida']} kWh")
    print(f"    Balanco            : {bal['balanco']:+.2f} kWh  [{bal['status']}]")
    print(f"    Bateria            : {bal['reserva']}%")
    print(f"    {bal['mensagem']}")

    print(f"\n  DECISOES")
    for acao in processado['acoes']:
        print(f"    {acao}")

    energia_prevista = prever(irradiancia_futura, a, b)
    print(f"\n  PREVISAO (regressao linear)")
    print(f"    Equacao            : energia = {a} * irradiancia + {b}")
    print(f"    Entrada            : irradiancia = {irradiancia_futura} W/m²")
    print(f"    Energia estimada   : {energia_prevista} kWh")

    _linha()