"""
estruturas.py - estruturas de dados do SIFSM (etapa 4).

  Fila de prioridade (heap) -> atender primeiro os alertas mais graves
  Pilha (list)              -> histórico de ações: a última ação aparece primeiro (LIFO)
  Tabela hash (dict)        -> busca rápida de módulo pelo código, O(1)
  Grafo (dict de listas)    -> dependência entre módulos e impacto de uma falha (BFS)
"""
import heapq
from collections import deque

import dados
import regras

# ---------------------------------------------------------------------------
# 1. PILHA: histórico de ações do CRUD (a última ação feita é a primeira a sair)
# ---------------------------------------------------------------------------
historico = []


def registrar_acao(texto):
    historico.append(texto)          # push


def mostrar_historico(limite=10):
    print("\n  Histórico (mais recente primeiro):")
    if not historico:
        print("  (nenhuma ação nesta sessão)")
    for acao in reversed(historico[-limite:]):
        print("   -", acao)


dados.ao_registrar = registrar_acao   # o CRUD avisa a pilha a cada operação


# ---------------------------------------------------------------------------
# 2. FILA DE PRIORIDADE (heap) para alertas
# ---------------------------------------------------------------------------
def montar_fila_alertas():
    """Heap de (-prioridade, ciclo, id): heapq é de mínimo, então o sinal negativo
    faz a maior prioridade sair primeiro. RISCO da regra booleana soma +1 na prioridade."""
    fila = []
    for r, x in regras.analisar_registros():
        if x["alerta"] or r["status"] == "alerta":
            prioridade = r["prioridade_alerta"] + (1 if x["risco"] else 0)
            heapq.heappush(fila, (-prioridade, -r["ciclo"], r["id"], r["codigo_modulo"],
                                  r["mensagem"]))
    return fila


def mostrar_fila_alertas():
    fila = montar_fila_alertas()
    print("\n  Alertas por prioridade (do mais urgente):")
    while fila:
        prio, ciclo, id_reg, modulo, msg = heapq.heappop(fila)
        print("   prioridade %d | ciclo %d | id %-3d | %s | %s" % (-prio, -ciclo, id_reg, modulo, msg))


# ---------------------------------------------------------------------------
# 3. TABELA HASH (dict): código do módulo -> dados do módulo
# ---------------------------------------------------------------------------
def indice_modulos():
    indice = {}
    for r in dados.consultar():
        indice.setdefault(r["codigo_modulo"], {"modulo": r["modulo"], "tipo": r["tipo"],
                                               "leituras": []})
        indice[r["codigo_modulo"]]["leituras"].append(r)
    return indice


def buscar_modulo(codigo):
    modulo = indice_modulos().get(codigo.strip().upper())   # busca direta pela chave
    if modulo is None:
        print("  Módulo não encontrado.")
        return
    consumos = [l["consumo_kwh"] for l in modulo["leituras"]]
    print("  %s (%s): %d leituras, consumo médio %.1f kWh, último nível de bateria %.1f%%" % (
        modulo["modulo"], modulo["tipo"], len(consumos), sum(consumos) / len(consumos),
        modulo["leituras"][-1]["bateria_pct"]))


# ---------------------------------------------------------------------------
# 4. GRAFO: quem depende de quem (seta A -> B significa "A fornece para B")
# ---------------------------------------------------------------------------
GRAFO = {
    "MOD-EN-001": ["MOD-SV-002", "MOD-HB-003", "MOD-SC-004", "MOD-MN-005",
                   "MOD-LG-006", "MOD-AG-007", "MOD-CM-008"],
    "MOD-MN-005": ["MOD-LG-006"],     # ISRU produz insumos para a logística
    "MOD-LG-006": ["MOD-AG-007"],     # logística abastece a agricultura
    "MOD-AG-007": ["MOD-SV-002"],     # agricultura sustenta o suporte à vida
    "MOD-CM-008": ["MOD-SC-004"],     # comunicação leva os dados dos sensores
    "MOD-SV-002": [], "MOD-HB-003": [], "MOD-SC-004": [],
}


def modulos_afetados(origem):
    """Busca em largura (BFS): todos os módulos que param se 'origem' falhar."""
    visitados, fila = set(), deque([origem])
    while fila:
        atual = fila.popleft()
        for vizinho in GRAFO.get(atual, []):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)
    return sorted(visitados)


def mostrar_impacto(codigo):
    codigo = codigo.strip().upper()
    if codigo not in GRAFO:
        print("  Módulo não encontrado no grafo.")
        return
    afetados = modulos_afetados(codigo)
    print("  Se %s falhar, %d módulo(s) são afetados: %s" % (
        codigo, len(afetados), ", ".join(afetados) or "nenhum"))


# ---------------------------------------------------------------------------
def menu_estruturas():
    while True:
        print("\n--- Estruturas de dados ---")
        print(" 1. Fila de alertas [heap]   2. Histórico [pilha]")
        print(" 3. Buscar módulo [hash]     4. Impacto de falha [grafo]   0. Voltar")
        op = input("Opção: ").strip()
        if op == "0":
            return
        elif op == "1":
            mostrar_fila_alertas()
        elif op == "2":
            mostrar_historico()
        elif op == "3":
            buscar_modulo(input("  Código do módulo (ex.: MOD-EN-001): "))
        elif op == "4":
            mostrar_impacto(input("  Módulo que falhou (ex.: MOD-MN-005): "))
        else:
            print("  Opção inválida.")
