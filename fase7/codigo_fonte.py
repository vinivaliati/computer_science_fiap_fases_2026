"""
SIFSM - Sistema Integrado de Futuro Sustentável em Marte
Colônia Aurora Siger | Fase 7 - "A Aurora Constrói os Alicerces de um Futuro Sustentável em Marte"
Arquivo principal: execute este arquivo (python codigo_fonte.py).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulos"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import dados
import regras
import estruturas
import simulacao_computacional
import modelo
import hardware
import agentes
import arquitetura
import analise

MENU = """
╔══════════════════════════════════════════════════════╗
║          SIFSM — Colônia Aurora Siger                ║
╠══════════════════════════════════════════════════════╣
║  1. Registros da colônia (CRUD)                      ║
║  2. Regras de decisão            [lógica booleana]   ║
║  3. Estruturas de dados    [heap, pilha, hash, grafo]║
║  4. Simulação da bateria        [integração]         ║
║  5. Modelo linear                [regressão]         ║
║  6. Circuito lógico / Arduino    [Tinkercad]         ║
║  7. Agentes de IA e guardrails   [Gemini]            ║
║  8. Arquitetura e desempenho     [CPU/GPU/NPU]       ║
║  9. Analisar sustentabilidade da colônia             ║
║  0. Sair                                             ║
╚══════════════════════════════════════════════════════╝"""


def main():
    dados.preparar()
    opcoes = {
        "1": dados.menu_crud,
        "2": regras.menu_regras,
        "3": estruturas.menu_estruturas,
        "4": simulacao_computacional.menu_simulacao,
        "5": modelo.menu_modelo,
        "6": hardware.menu_hardware,
        "7": agentes.menu_agentes,
        "8": arquitetura.menu_arquitetura,
        "9": analise.analise_final,
    }
    while True:
        print(MENU)
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            print("Encerrando o SIFSM. Até a próxima missão!")
            break
        elif escolha in opcoes:
            try:
                opcoes[escolha]()
            except Exception as erro:   
                print("\n  Ocorreu um erro inesperado: %s" % erro)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
