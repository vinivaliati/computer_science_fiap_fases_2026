import random

from src.dados     import SISTEMAS_COLONIA
from data.gerar     import gerar_dados
from src.decisao   import decidir
from src.energia   import analisar_balanco
from src.previsao  import calcular_regressao
from src.relatorio import imprimir_cabecalho, imprimir_hierarquia, imprimir_resumo, imprimir_detalhe


def processar(registros):
    return [
        {
            'registro': r,
            'balanco':  analisar_balanco(r),
            'acoes':    decidir(r),
        }
        for r in registros
    ]


def main():
    imprimir_cabecalho()

    registros  = gerar_dados()
    processados = processar(registros)
    a, b       = calcular_regressao(registros)

    print("\n--- HIERARQUIA DE SISTEMAS ---")
    imprimir_hierarquia(SISTEMAS_COLONIA)

    imprimir_resumo(processados)

    sorteado = random.choice(processados)
    imprimir_detalhe(sorteado, a, b)


if __name__ == '__main__':
    main()