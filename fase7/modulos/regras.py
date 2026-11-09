"""
regras.py - lógica booleana e regras de decisão da colônia (etapa 3).

Variáveis (entradas, cada uma é True ou False):
    B = bateria baixa      (bateria_pct < 25)
    E = módulo essencial   (energia, suporte à vida ou habitação)
    C = consumo alto       (consumo > 120% da média do próprio módulo)
    T = temperatura alta   (temperatura_c > 26)

Expressões lógicas (saídas):
    RISCO  = (B AND E) OR (C AND T)   -> liga LED vermelho + buzzer
    ALERTA = B OR C OR T              -> liga LED amarelo
Os mesmos 4 sinais serão usados no circuito do Tinkercad (etapa 6).
"""
import dados

LIMITE_BATERIA = 25.0       # %
LIMITE_TEMPERATURA = 26.0   # °C
FATOR_CONSUMO = 1.20        # 120% da média do módulo
TIPOS_ESSENCIAIS = ("energia", "suporte à vida", "habitação")


def avaliar(bateria_baixa, essencial, consumo_alto, temperatura_alta):
    """Aplica as duas expressões booleanas. Devolve (risco, alerta)."""
    risco = (bateria_baixa and essencial) or (consumo_alto and temperatura_alta)
    alerta = bateria_baixa or consumo_alto or temperatura_alta
    return risco, alerta


def classificar(registro, media_consumo):
    """Transforma um registro do banco nas 4 variáveis booleanas e aplica a regra."""
    b = registro["bateria_pct"] < LIMITE_BATERIA
    e = registro["tipo"] in TIPOS_ESSENCIAIS
    c = registro["consumo_kwh"] > FATOR_CONSUMO * media_consumo
    t = registro["temperatura_c"] > LIMITE_TEMPERATURA
    risco, alerta = avaliar(b, e, c, t)
    return {"B": b, "E": e, "C": c, "T": t, "risco": risco, "alerta": alerta}


def medias_por_modulo(registros):
    """Média de consumo de cada módulo (dicionário código -> média)."""
    somas = {}
    for r in registros:
        soma, qtd = somas.get(r["codigo_modulo"], (0.0, 0))
        somas[r["codigo_modulo"]] = (soma + r["consumo_kwh"], qtd + 1)
    return {cod: soma / qtd for cod, (soma, qtd) in somas.items()}


def analisar_registros():
    """Classifica todos os registros do banco. Devolve lista de (registro, resultado)."""
    registros = dados.consultar()
    medias = medias_por_modulo(registros)
    return [(r, classificar(r, medias[r["codigo_modulo"]])) for r in registros]


def tabela_verdade():
    """Imprime a tabela verdade completa (16 linhas) das duas expressões."""
    print("\n  B E C T | RISCO ALERTA")
    print("  --------+-------------")
    for n in range(16):
        b, e, c, t = (bool(n & 8), bool(n & 4), bool(n & 2), bool(n & 1))
        risco, alerta = avaliar(b, e, c, t)
        print("  %d %d %d %d |   %d      %d" % (b, e, c, t, risco, alerta))


def circuito_ascii():
    print("""
  Circuito lógico (portas):

   B ──┐
       AND ──┐
   E ──┘     │
             OR ──────► RISCO  (LED vermelho + buzzer)
   C ──┐     │
       AND ──┘
   T ──┘

   B ──┐
   C ──┼─ OR (3 entradas) ──► ALERTA (LED amarelo)
   T ──┘
""")


def exibir_analise():
    resultado = analisar_registros()
    print("\n  %-4s %-11s %-5s  B E C T  Situação" % ("ID", "Módulo", "Ciclo"))
    contagem = {"RISCO": 0, "ALERTA": 0, "NORMAL": 0}
    for r, x in resultado:
        situacao = "RISCO" if x["risco"] else ("ALERTA" if x["alerta"] else "NORMAL")
        contagem[situacao] += 1
        if situacao != "NORMAL":
            print("  %-4d %-11s %-5d  %d %d %d %d  %s" % (
                r["id"], r["codigo_modulo"], r["ciclo"], x["B"], x["E"], x["C"], x["T"], situacao))
    print("\n  Total: %d em RISCO, %d em ALERTA, %d normais (de %d registros)." % (
        contagem["RISCO"], contagem["ALERTA"], contagem["NORMAL"], len(resultado)))


def menu_regras():
    while True:
        print("\n--- Regras de decisão (lógica booleana) ---")
        print(" 1. Analisar registros   2. Tabela verdade   3. Circuito lógico   0. Voltar")
        op = input("Opção: ").strip()
        if op == "0":
            return
        elif op == "1":
            exibir_analise()
        elif op == "2":
            tabela_verdade()
        elif op == "3":
            circuito_ascii()
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    dados.preparar()
    exibir_analise()
