"""
agentes.py - agentes de IA com ferramentas, handoffs, guardrails e tracing.

Fluxo:  Pedido -> [guardrail de entrada] -> Agente MONITOR -> handoff -> Agente ANALISTA
        -> handoff -> Agente PLANEJADOR -> [guardrail de saída] -> HUMANO decide

* Cada agente é uma chamada ao modelo (llm.py) com um papel (instrução) e uma lista PERMITIDA
  de ferramentas. As ferramentas são funções nossas, somente leitura/cálculo: nenhuma altera o banco.
* O modelo decide quais ferramentas chamar (function calling); nosso código valida os argumentos.
* Privacidade: só vão para a API dados agregados e simulados de módulos (nada de pessoas).
* Se não houver chave/rede, o sistema usa o FLUXO SIMULADO (determinístico) e avisa isso na tela.
"""
import regras
import estruturas
import simulacao_computacional as sim
import llm

# ---------------------------------------------------------------------------
# Base de conhecimento simples (RAG conceitual: busca por tema e cita a fonte)
# ---------------------------------------------------------------------------
PROCEDIMENTOS = {
    "bateria": "PROC-01: bateria < 25% em módulo essencial -> priorizar recarga e reduzir cargas não essenciais.",
    "consumo": "PROC-02: consumo > 120% da média -> verificar equipamentos e reagendar tarefas pesadas para o dia.",
    "temperatura": "PROC-03: temperatura > 26 °C -> checar ventilação e isolamento do módulo.",
    "tempestade": "PROC-04: tempestade de poeira -> entrar em modo econômico e proteger o suporte à vida.",
}

trace = []  


def registrar(agente, acao):
    trace.append("[%s] %s" % (agente, acao))


# ---------------------------------------------------------------------------
# Ferramentas (somente leitura/cálculo). Os argumentos vindos do modelo são VALIDADOS.
# ---------------------------------------------------------------------------
def ferramenta_listar_alertas():
    return [{"modulo": r["codigo_modulo"], "ciclo": r["ciclo"], "risco": bool(x["risco"]),
             "bateria_pct": r["bateria_pct"], "consumo_kwh": r["consumo_kwh"],
             "temperatura_c": r["temperatura_c"]}
            for r, x in regras.analisar_registros() if x["alerta"]]


def ferramenta_simular_cenario(ciclo=None, fator_geracao=1.0):
    """Sem ciclo informado, simula o ciclo mais crítico da colônia."""
    ciclo = sim.ciclo_mais_critico() if ciclo is None else int(ciclo)
    fator_geracao = float(fator_geracao)
    if not 1 <= ciclo <= 1000:
        raise ValueError("ciclo fora do intervalo")
    if not 0.0 <= fator_geracao <= 1.5:
        raise ValueError("fator_geracao deve estar entre 0 e 1.5")
    r = sim.simular(ciclo, fator_geracao)
    return {"ciclo": ciclo, "fator_geracao": fator_geracao, "soc_final_pct": round(r["soc_final"], 1),
            "soc_minimo_pct": round(r["soc_min"], 1), "horas_abaixo_de_20pct": round(r["horas_criticas"], 1)}


def ferramenta_impacto_falha(codigo_modulo):
    codigo = str(codigo_modulo).strip().upper()
    if codigo not in estruturas.GRAFO:
        raise ValueError("módulo desconhecido")
    return {"modulo": codigo, "modulos_afetados": estruturas.modulos_afetados(codigo)}


def ferramenta_buscar_procedimento(tema):
    tema = str(tema).lower()
    return [texto for chave, texto in PROCEDIMENTOS.items() if chave in tema or tema in chave]


def _decl(nome, descricao, propriedades=None, obrigatorios=()):
    declaracao = {"name": nome, "description": descricao}
    if propriedades:
        declaracao["parameters"] = {"type": "OBJECT", "properties": propriedades,
                                    "required": list(obrigatorios)}
    return declaracao


# Allowlist por agente: cada um só enxerga as ferramentas do seu papel.
FERRAMENTAS = {
    "Monitor": {"listar_alertas": {
        "funcao": ferramenta_listar_alertas,
        "declaracao": _decl("listar_alertas", "Lista as leituras dos módulos que estão em alerta ou risco.")}},
    "Analista": {"simular_cenario": {
        "funcao": ferramenta_simular_cenario,
        "declaracao": _decl("simular_cenario",
                            "Simula o estado de carga da bateria da colônia em um ciclo. "
                            "Sem ciclo, usa o ciclo mais crítico. fator_geracao 1.0 = normal; 0.4 = tempestade de poeira.",
                            {"ciclo": {"type": "INTEGER"}, "fator_geracao": {"type": "NUMBER"}})}},
    "Planejador": {
        "impacto_falha": {
            "funcao": ferramenta_impacto_falha,
            "declaracao": _decl("impacto_falha", "Diz quais módulos são afetados se um módulo falhar.",
                                {"codigo_modulo": {"type": "STRING"}}, ["codigo_modulo"])},
        "buscar_procedimento": {
            "funcao": ferramenta_buscar_procedimento,
            "declaracao": _decl("buscar_procedimento",
                                "Busca procedimentos oficiais por tema: bateria, consumo, temperatura ou tempestade.",
                                {"tema": {"type": "STRING"}}, ["tema"])}},
}

INSTRUCOES = {
    "Monitor": ("Você é o agente MONITOR da colônia Aurora Siger. Use a ferramenta listar_alertas e "
                "resuma em até 5 linhas, em português, quais módulos e ciclos estão em risco ou alerta. "
                "Não invente dados."),
    "Analista": ("Você é o agente ANALISTA de energia da Aurora Siger. Com base no resumo do Monitor, "
                 "use simular_cenario sem informar o ciclo (a ferramenta escolhe o mais crítico), uma vez normal "
                 "e uma vez com fator_geracao 0.4, "
                 "e explique em até 5 linhas o risco para a bateria. Não invente números: use só os das ferramentas."),
    "Planejador": ("Você é o agente PLANEJADOR da Aurora Siger. Use impacto_falha nos módulos em risco e "
                   "buscar_procedimento para citar os procedimentos (PROC-xx). Escreva uma recomendação "
                   "técnica curta em português (até 8 linhas). Você apenas SUGERE; nunca diga que executou ações."),
}


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------
PALAVRAS_PROIBIDAS = ("excluir", "apagar", "alterar", "desligar", "drop")


def guardrail_entrada(pedido):
    """Bloqueia pedidos que tentam mudar dados/ações físicas ou acessar dados pessoais."""
    texto = pedido.lower()
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra in texto:
            return False, "Bloqueado: os agentes só têm permissão de leitura/análise ('%s')." % palavra
    if "nome" in texto and "tripul" in texto:
        return False, "Bloqueado: dados pessoais de tripulantes não são acessados (privacidade)."
    if len(pedido) > 300:
        return False, "Bloqueado: pedido muito longo."
    return True, "ok"


def guardrail_saida(texto):
    """Toda recomendação sai marcada como sugestão e exige aprovação humana."""
    return texto + "\n  [GUARDRAIL] Esta é uma SUGESTÃO. Precisa de aprovação do operador humano."


# ---------------------------------------------------------------------------
# Fluxo com LLM real (Gemini)
# ---------------------------------------------------------------------------
def fluxo_llm(pedido, chamar=None):
    registrar("Sessão", "modelo: %s" % llm.MODELO)
    resumo = llm.executar_agente("Monitor", INSTRUCOES["Monitor"], pedido,
                                 FERRAMENTAS["Monitor"], registrar, chamar)
    registrar("Monitor", "handoff -> Analista")
    analise = llm.executar_agente("Analista", INSTRUCOES["Analista"],
                                  "Pedido: %s\n\nResumo do Monitor:\n%s" % (pedido, resumo),
                                  FERRAMENTAS["Analista"], registrar, chamar)
    registrar("Analista", "handoff -> Planejador")
    return llm.executar_agente("Planejador", INSTRUCOES["Planejador"],
                               "Pedido: %s\n\nMonitor:\n%s\n\nAnalista:\n%s" % (pedido, resumo, analise),
                               FERRAMENTAS["Planejador"], registrar, chamar)


# ---------------------------------------------------------------------------
# Fluxo simulado (fallback determinístico, sem modelo de linguagem)
# ---------------------------------------------------------------------------
def fluxo_simulado():
    alertas = ferramenta_listar_alertas()
    registrar("Monitor", "(simulado) %d alertas" % len(alertas))
    riscos = [a for a in alertas if a["risco"]]
    registrar("Analista", "(simulado) %d riscos" % len(riscos))
    linhas = []
    if not riscos:
        linhas.append("Nenhum risco ativo. Manter monitoramento.")
    for a in riscos:
        afetados = ferramenta_impacto_falha(a["modulo"])["modulos_afetados"]
        linhas.append("- %s (ciclo %d) em RISCO. Se falhar, afeta: %s" % (
            a["modulo"], a["ciclo"], ", ".join(afetados) or "nenhum módulo"))
    s = ferramenta_simular_cenario(None, 0.4)
    linhas.append("- Em tempestade de poeira (ciclo %d, o mais crítico) o SoC mínimo cairia a %.1f%%." % (
        s["ciclo"], s["soc_minimo_pct"]))
    for tema in ("bateria", "consumo", "tempestade"):
        for proc in ferramenta_buscar_procedimento(tema):
            linhas.append("  Fonte: " + proc)
    registrar("Planejador", "(simulado) recomendação montada")
    return "\n".join(linhas)


def executar_fluxo(pedido, usar_llm=True, chamar=None):
    trace.clear()
    registrar("Sessão", "pedido: " + pedido)
    permitido, motivo = guardrail_entrada(pedido)
    if not permitido:
        registrar("Guardrail", motivo)
        print("\n  " + motivo)
        return
    origem = "simulado"
    try:
        if not usar_llm:
            raise llm.LLMIndisponivel("modo simulado escolhido")
        print("\n  Consultando o Gemini (são enviados só dados simulados e agregados de módulos)...")
        texto = fluxo_llm(pedido, chamar)
        origem = "Gemini (%s)" % llm.MODELO
    except llm.LLMIndisponivel as erro:
        registrar("Sistema", "LLM indisponível (%s) -> fluxo simulado" % erro)
        print("  [simulado - %s]" % erro)
        texto = fluxo_simulado()
    except Exception as erro:   # qualquer outra falha também não pode derrubar o menu
        registrar("Sistema", "erro inesperado (%s) -> fluxo simulado" % erro)
        print("  [simulado - erro inesperado: %s]" % erro)
        texto = fluxo_simulado()
    print("\n  === Recomendação (origem: %s) ===\n%s" % (origem, guardrail_saida(texto)))


def mostrar_trace():
    print("\n  === Tracing do último fluxo ===")
    for linha in trace:
        print("   ", linha)


def menu_agentes():
    print(__doc__)
    while True:
        print("\n--- Agentes de IA ---")
        print(" 1. Pedir análise (Gemini)   2. Pedir análise (simulado)   3. Ver tracing   0. Voltar")
        op = input("Opção: ").strip()
        if op == "0":
            return
        elif op in ("1", "2"):
            usar = op == "1" and llm.garantir_chave_api()
            pedido = input("  Pedido (ex.: 'analisar riscos de energia'; tente 'excluir registros'): ")
            executar_fluxo(pedido.strip() or "analisar riscos de energia", usar_llm=usar)
        elif op == "3":
            mostrar_trace()
        else:
            print("  Opção inválida.")
