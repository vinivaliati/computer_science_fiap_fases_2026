# =============================================================================
# NCAS - NUCLEO COGNITIVO DA AURORA SIGER
# Cap 1 - Inteligencia Artificial no Comando | Fase 5
# =============================================================================

import json
from datetime import datetime

# === [1] CONSTANTES E CAMINHOS DE ARQUIVO ===
ARQUIVO_JSON = "dados_colonia.json"
ARQUIVO_LOG = "registros_colonia.txt"

# === [2] CAMADA DE DADOS - JSON === 

def carregar_dados():
    """Le o arquivo JSON do disco e devolve um dicionario Python."""
    with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados):
    """Grava o dicionario Python de volta no arquivo JSON."""
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)

#  === [3] CAMADA DE DADOS - TEXTO (LOG DE INTERACOES) ===

def registrar_log(tipo_evento, descricao):
    """adicona UMA linha ao log, sem apagar o que ja existe."""
    momento=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{momento} [{tipo_evento}] {descricao}\n"
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(linha)
    
def abrir_sessao():
    """Grava de uma vez o bloco de linhas que marca o inicio de uma sessao"""
    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        f"[{momento}] SESSAO: inicio de sessao de NCAS \n",
        f"[{momento}] SISTEMA: SESSAO: dados carregados de {ARQUIVO_JSON}\n", 
        ]
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
          arquivo.writelines(linhas)

def ler_logs():
    """Devolve TODAS as linhas de log com uma lista de strings"""
    try:
        with open(ARQUIVO_LOG, "r", encoding="utf-8") as arquivo:
            return arquivo.readlines()
    except FileNotFoundError:
        return []

def primeiro_registro():
    """Le apenas a PRIMEIRA linha de log: quando o sistema comeca a ser usado"""
    try:
        with open(ARQUIVO_LOG, "r", encoding="utf-8") as arquivo:
            return arquivo.readline().rstrip() 
    except FileNotFoundError:
        return "LOG: arquivo de log ainda nao criado."

def tamanho_log():
    """Le o log INTEIRO como um unico texto e devolve quantos caracteres ele ocupa."""
    try:
        with open (ARQUIVO_LOG,"r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
            return len(conteudo)
    except FileNotFoundError:
        return 0

def exibir_logs(quantidade=10):
    """Mostra na tela os ultimos registros do log"""
    linhas = ler_logs()
    if not linhas:
        print("Nenhum registro encontrado")
        return
    print(f"\n--- ULTIMOS {min(quantidade, len(linhas))} REGISTROS ---")
    for linha in linhas[-quantidade:]:
        print(linha.rstrip())
    print(f"(log com {len(linhas)} linhas e {tamanho_log()} caracteres)")
    print(f"(primeiro registro: {primeiro_registro()})")

# === [4] REGISTROS: BUSCA, CADASTRO E CONSULTA 

def buscar_modulo(dados, nome):
    """Procura um modulo pelo nome. Devolve o dicionario ou None."""
    for modulo in dados["modulos"]:
        if modulo["nome"] == nome:
            return modulo
    return None


def buscar_alerta(dados, alerta_id):
    """Procura um alerta pelo id. Devolve o dicionario ou None."""
    for alerta in dados["alertas"]:
        if alerta["id"] == alerta_id:
            return alerta
    return None


def proximo_id(dados):
    """Devolve o proximo id livre da lista de alertas."""
    if not dados["alertas"]:
        return 1
    return max(alerta["id"] for alerta in dados["alertas"]) + 1


def cadastrar_alerta(dados, modulo, tipo_ocorrencia, prioridade, data,
                     mensagem, falha_detectada, consumo_elevado):
    """Cria um alerta, guarda na lista, salva no JSON e registra no log."""
    alerta = {
        "id": proximo_id(dados),
        "modulo": modulo,
        "tipo_ocorrencia": tipo_ocorrencia,
        "prioridade": prioridade,
        "data": data,
        "mensagem": mensagem,
        "falha_detectada": falha_detectada,
        "consumo_elevado": consumo_elevado,
    }
    dados["alertas"].append(alerta)
    salvar_dados(dados)
    registrar_log("CADASTRO", f"alerta #{alerta['id']} criado no modulo {modulo}")
    return alerta


def listar_modulos(dados):
    """Mostra na tela todos os modulos da colonia."""
    print(f"\n--- MODULOS DA COLONIA ({len(dados['modulos'])}) ---")
    for modulo in dados["modulos"]:
        print(f"{modulo['nome']:<26} | {modulo['consumo_kw']:>3} kW | "
              f"{modulo['status']:<12} | {modulo['prioridade_operacional']}")
    registrar_log("CONSULTA", "listagem de modulos exibida")


def listar_alertas(dados):
    """Mostra na tela todos os alertas registrados."""
    print(f"\n--- ALERTAS REGISTRADOS ({len(dados['alertas'])}) ---")
    if not dados["alertas"]:
        print("Nenhum alerta cadastrado.")
        return
    for alerta in dados["alertas"]:
        print(f"#{alerta['id']:<3} [{alerta['prioridade']:^6}] "
              f"{alerta['data']} | {alerta['modulo']}")
        print(f"      {alerta['mensagem']}")
    registrar_log("CONSULTA", "listagem de alertas exibida")

# === [5] REGRAS LOGICAS E SIMPLIFICACAO BOOLEANA === 
# As funcoes "_original" ficam no codigo apenas para provar, via
# tabela_verdade(), que a versao simplificada da o mesmo resultado.


# REGRA A - criticidade do alerta (propriedade distributiva)
#   Original:  CRITICO = (FALHA AND MOD_CRITICO) OR (FALHA AND CONSUMO_ALTO)
#   Simplif.:  CRITICO = FALHA AND (MOD_CRITICO OR CONSUMO_ALTO)
#   FALHA em evidencia: 3 operacoes viram 2, com o mesmo resultado logico.

def eh_critico(falha, mod_critico, consumo_alto):
    """Versao SIMPLIFICADA da regra de criticidade. E esta que o sistema usa."""
    return falha and (mod_critico or consumo_alto)


def eh_critico_original(falha, mod_critico, consumo_alto):
    """Versao ORIGINAL, mantida apenas para provar a equivalencia."""
    return (falha and mod_critico) or (falha and consumo_alto)


# REGRA B - bloqueio de acesso (Teorema de De Morgan)
#   Original:   BLOQUEAR = NOT (AUTORIZADO AND MODULO_ATIVO)
#   De Morgan:  BLOQUEAR = (NOT AUTORIZADO) OR (NOT MODULO_ATIVO)
#   As duas causas ficam separadas, permitindo informar QUAL bloqueou.

def bloquear_acesso(autorizado, modulo_ativo):
    """Versao SIMPLIFICADA (De Morgan). E esta que o sistema usa."""
    return (not autorizado) or (not modulo_ativo)


def bloquear_acesso_original(autorizado, modulo_ativo):
    """Versao ORIGINAL, mantida apenas para provar a equivalencia."""
    return not (autorizado and modulo_ativo)


def tabela_verdade():
    """Imprime as tabelas-verdade que provam a equivalencia das duas formas."""
    print("\n--- REGRA A: CRITICIDADE ---")
    print(f"{'FALHA':<8}{'MOD_CRIT':<10}{'CONS_ALTO':<11}"
          f"{'ORIGINAL':<10}{'SIMPLIF.':<10}IGUAIS")
    for falha in (False, True):
        for mod_critico in (False, True):
            for consumo_alto in (False, True):
                original = eh_critico_original(falha, mod_critico, consumo_alto)
                simples = eh_critico(falha, mod_critico, consumo_alto)
                print(f"{str(falha):<8}{str(mod_critico):<10}{str(consumo_alto):<11}"
                      f"{str(original):<10}{str(simples):<10}{original == simples}")

    print("\n--- REGRA B: BLOQUEIO DE ACESSO (DE MORGAN) ---")
    print(f"{'AUTORIZ.':<10}{'MOD_ATIVO':<11}"
          f"{'ORIGINAL':<10}{'SIMPLIF.':<10}IGUAIS")
    for autorizado in (False, True):
        for modulo_ativo in (False, True):
            original = bloquear_acesso_original(autorizado, modulo_ativo)
            simples = bloquear_acesso(autorizado, modulo_ativo)
            print(f"{str(autorizado):<10}{str(modulo_ativo):<11}"
                  f"{str(original):<10}{str(simples):<10}{original == simples}")

    registrar_log("LOGICA", "tabelas verdade exibidas")

# === [6] PROMPTS ESTRUTURADOS === 

def condicoes_do_alerta(dados, alerta):
    """Extrai do alerta e do seu modulo as tres condicoes da Regra A."""
    modulo = buscar_modulo(dados, alerta["modulo"])
    falha = alerta["falha_detectada"]
    mod_critico = modulo is not None and modulo["prioridade_operacional"] == "CRITICA"
    consumo_alto = alerta["consumo_elevado"]
    return falha, mod_critico, consumo_alto


def prompt_zero_shot(alerta):
    """ZERO-SHOT: instrucao direta, sem exemplos."""
    return (
        "Voce e o assistente do Nucleo Cognitivo da colonia Aurora Siger.\n"
        "Resuma o alerta abaixo em uma frase objetiva para o Centro de Comando.\n\n"
        f"Modulo: {alerta['modulo']}\n"
        f"Ocorrencia: {alerta['tipo_ocorrencia']}\n"
        f"Mensagem: {alerta['mensagem']}"
    )


def prompt_few_shot(alerta):
    """FEW-SHOT: exemplos resolvidos antes da tarefa real."""
    return (
        "Classifique a urgencia do alerta como URGENTE, MODERADA ou BAIXA.\n\n"
        "Alerta: 'Falha no suporte a vida do Habitat A' -> Urgencia: URGENTE\n"
        "Alerta: 'Consumo 10% acima da media na estufa' -> Urgencia: MODERADA\n"
        "Alerta: 'Pedido de ajuste de temperatura no dormitorio' -> Urgencia: BAIXA\n\n"
        f"Alerta: '{alerta['mensagem']}' -> Urgencia:"
    )


def prompt_chain_of_thought(dados, alerta):
    """CHAIN-OF-THOUGHT: pede o raciocinio passo a passo antes da conclusao."""
    modulo = buscar_modulo(dados, alerta["modulo"])
    prioridade = modulo["prioridade_operacional"] if modulo else "DESCONHECIDA"
    return (
        "Decida se o alerta e CRITICO, pensando passo a passo:\n"
        "1. Ha falha detectada?\n"
        "2. O modulo tem prioridade operacional CRITICA?\n"
        "3. Ha consumo elevado?\n"
        "4. Conclua: e critico se houver FALHA E (MODULO CRITICO OU CONSUMO ELEVADO).\n\n"
        f"Modulo: {alerta['modulo']} (prioridade {prioridade})\n"
        f"Falha detectada: {alerta['falha_detectada']}\n"
        f"Consumo elevado: {alerta['consumo_elevado']}"
    )


def prompt_structured_output(dados, alerta):
    """STRUCTURED OUTPUT: exige a resposta em JSON com chaves fixas."""
    modulo = buscar_modulo(dados, alerta["modulo"])
    prioridade = modulo["prioridade_operacional"] if modulo else "DESCONHECIDA"
    return (
        "Analise o alerta e responda APENAS com um objeto JSON valido, "
        "sem texto antes ou depois, com exatamente estas chaves:\n"
        '{"modulo": str, "criticidade": "CRITICO" ou "NORMAL", '
        '"urgencia": "URGENTE" ou "MODERADA" ou "BAIXA", "acao_recomendada": str}\n\n'
        f"Modulo: {alerta['modulo']} (prioridade {prioridade})\n"
        f"Falha detectada: {alerta['falha_detectada']}\n"
        f"Consumo elevado: {alerta['consumo_elevado']}\n"
        f"Mensagem: {alerta['mensagem']}"
    )


def exibir_prompts(dados, alerta):
    """Mostra na tela os quatro prompts montados para um alerta."""
    print(f"\n=== PROMPTS ESTRUTURADOS | ALERTA #{alerta['id']} ===")
    print("\n--- 1. ZERO-SHOT ---")
    print(prompt_zero_shot(alerta))
    print("\n--- 2. FEW-SHOT ---")
    print(prompt_few_shot(alerta))
    print("\n--- 3. CHAIN-OF-THOUGHT ---")
    print(prompt_chain_of_thought(dados, alerta))
    print("\n--- 4. STRUCTURED OUTPUT ---")
    print(prompt_structured_output(dados, alerta))
    registrar_log("PROMPT", f"prompts exibidos para o alerta #{alerta['id']}")


# === [7] SIMULACAO DA RESPOSTA DO ASSISTENTE ===
# Sem API real. A resposta e derivada dos dados do alerta e das regras
# logicas do sistema; apenas a redacao final e predefinida.


def classificar_urgencia(critico, prioridade_alerta):
    """Traduz criticidade + prioridade declarada em um rotulo de urgencia."""
    if critico:
        return "URGENTE"
    if prioridade_alerta == "alta":
        return "MODERADA"
    return "BAIXA"


def acao_recomendada(critico, modulo_ativo):
    """Escolhe a acao sugerida ao Centro de Comando."""
    if critico:
        return "Acionar equipe tecnica imediatamente e notificar o Centro de Comando."
    if not modulo_ativo:
        return "Programar inspecao: o modulo esta fora de operacao."
    return "Registrar em relatorio de rotina e monitorar no proximo ciclo."


def simular_resposta(dados, alerta, tipo):
    """Simula a resposta do assistente para um dos quatro tipos de prompt."""
    falha, mod_critico, consumo_alto = condicoes_do_alerta(dados, alerta)
    critico = eh_critico(falha, mod_critico, consumo_alto)
    modulo = buscar_modulo(dados, alerta["modulo"])
    modulo_ativo = modulo is not None and modulo["status"] == "OPERACIONAL"
    urgencia = classificar_urgencia(critico, alerta["prioridade"])

    if tipo == "zero_shot":
        return (f"{alerta['modulo']}: {alerta['tipo_ocorrencia'].lower()} "
                f"registrada em {alerta['data']}.")

    if tipo == "few_shot":
        return urgencia

    if tipo == "chain_of_thought":
        return (
            f"1. Falha detectada: {falha}\n"
            f"2. Modulo com prioridade CRITICA: {mod_critico}\n"
            f"3. Consumo elevado: {consumo_alto}\n"
            f"4. FALHA AND (MOD_CRITICO OR CONSUMO_ALTO) = {critico}\n"
            f"Conclusao: alerta {'CRITICO' if critico else 'NORMAL'}."
        )

    if tipo == "structured":
        resposta = {
            "modulo": alerta["modulo"],
            "criticidade": "CRITICO" if critico else "NORMAL",
            "urgencia": urgencia,
            "acao_recomendada": acao_recomendada(critico, modulo_ativo),
        }
        return json.dumps(resposta, indent=2, ensure_ascii=False)

    return "Tipo de prompt desconhecido."


def comparar_prompts(dados, alerta):
    """Analise de otimizacao: prompt vago x prompt refinado."""
    print("\n=== ANALISE DE OTIMIZACAO DE PROMPT ===")

    print("\n[1] PROMPT VAGO")
    print(f"O que houve com o {alerta['modulo']}?")
    print("\n[1] RESPOSTA ESPERADA - generica, sem estrutura, nao verificavel")
    print("Houve um problema no modulo. Recomenda-se verificar.")

    print("\n[2] PROMPT REFINADO")
    print(prompt_structured_output(dados, alerta))
    print("\n[2] RESPOSTA - estruturada, derivada da regra logica, verificavel")
    print(simular_resposta(dados, alerta, "structured"))

    print("\nO refinamento reduz o erro da resposta ao restringir o espaco de saida:")
    print("papel definido, dados injetados, formato exigido e criterio de decisao explicito.")
    registrar_log("OTIMIZACAO", f"comparacao de prompts do alerta #{alerta['id']}")
                            
# === [8] FUNCIONALIDADE-VITRINE: ANALISAR ALERTA OPERACIONAL ===
# Integra tudo: carrega o alerta do JSON, aplica a Regra B (De Morgan) no
# controle de acesso, a Regra A (simplificacao) na criticidade e exibe o
# prompt estruturado com a resposta simulada do assistente.

def analisar_alerta(dados, alerta_id, autorizado=True):
    """Analise completa de um alerta operacional."""
    alerta = buscar_alerta(dados, alerta_id)
    if alerta is None:
        print(f"\nAlerta #{alerta_id} nao encontrado.")
        registrar_log("ERRO", f"analise pedida para alerta inexistente #{alerta_id}")
        return

    modulo = buscar_modulo(dados, alerta["modulo"])
    modulo_ativo = modulo is not None and modulo["status"] == "OPERACIONAL"

    print(f"\n=== ANALISE DO ALERTA #{alerta['id']} ===")
    print(f"Modulo    : {alerta['modulo']}")
    print(f"Ocorrencia: {alerta['tipo_ocorrencia']}")
    print(f"Mensagem  : {alerta['mensagem']}")

    # --- REGRA B (De Morgan): o acesso ao modulo e permitido? ---
    print("\n[REGRA B] BLOQUEAR = (NOT AUTORIZADO) OR (NOT MODULO_ATIVO)")
    print(f"          autorizado={autorizado} | modulo_ativo={modulo_ativo}")
    if bloquear_acesso(autorizado, modulo_ativo):
        if not autorizado:
            print("ACESSO NEGADO: usuario sem autorizacao.")
        else:
            print(f"ACESSO NEGADO: o modulo {alerta['modulo']} esta INATIVO.")
        registrar_log("BLOQUEIO", f"acesso negado ao alerta #{alerta['id']}")
        return
    print("Acesso liberado.")

    # --- REGRA A (simplificacao): o alerta e critico? ---
    falha, mod_critico, consumo_alto = condicoes_do_alerta(dados, alerta)
    critico = eh_critico(falha, mod_critico, consumo_alto)
    print("\n[REGRA A] CRITICO = FALHA AND (MOD_CRITICO OR CONSUMO_ALTO)")
    print(f"          falha={falha} | mod_critico={mod_critico} | consumo_alto={consumo_alto}")
    print(f"CLASSIFICACAO: {'CRITICO' if critico else 'NORMAL'}")

    # --- Prompt estruturado e resposta simulada ---
    print("\n--- PROMPT ENVIADO AO ASSISTENTE ---")
    print(prompt_structured_output(dados, alerta))
    print("\n--- RESPOSTA DO ASSISTENTE ---")
    print(simular_resposta(dados, alerta, "structured"))
    print("\nA decisao final e responsabilidade da equipe humana do Centro de Comando.")

    registrar_log("ANALISE", f"alerta #{alerta['id']} analisado: critico={critico}")

# [9] INTERFACE: MENU DE NAVEGACAO NO TERMINAL

def ler_inteiro(mensagem):
    """Le um numero inteiro do teclado, insistindo ate receber um valido."""
    while True:
        texto = input(mensagem).strip()
        if texto.isdigit():
            return int(texto)
        print("Entrada invalida: digite apenas numeros.")


def ler_sim_nao(mensagem):
    """Le uma resposta S/N do teclado e devolve True/False."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao"):
            return False
        print("Entrada invalida: responda com S ou N.")


def pedir_alerta(dados):
    """Pede um id ao usuario e devolve o alerta, ou None se nao existir."""
    alerta_id = ler_inteiro("Id do alerta: ")
    alerta = buscar_alerta(dados, alerta_id)
    if alerta is None:
        print(f"Alerta #{alerta_id} nao encontrado.")
    return alerta


def menu_cadastrar(dados):
    """Coleta os campos de um alerta pelo teclado e cadastra."""
    print("\n--- CADASTRAR ALERTA OPERACIONAL ---")
    nome = input("Modulo: ").strip()
    if buscar_modulo(dados, nome) is None:
        print(f"O modulo '{nome}' nao existe na colonia.")
        print("Use a opcao 2 para ver a lista de modulos validos.")
        return
    tipo_ocorrencia = input("Tipo de ocorrencia: ").strip()
    prioridade = input("Prioridade (alta/media/baixa): ").strip().lower()
    data = input("Data (AAAA-MM-DD): ").strip()
    mensagem = input("Mensagem: ").strip()
    falha = ler_sim_nao("Ha falha detectada? (S/N): ")
    consumo = ler_sim_nao("Ha consumo elevado? (S/N): ")
    alerta = cadastrar_alerta(dados, nome, tipo_ocorrencia, prioridade,
                              data, mensagem, falha, consumo)
    print(f"\nAlerta #{alerta['id']} cadastrado e salvo em {ARQUIVO_JSON}.")


def exibir_menu():
    """Desenha o menu principal na tela."""
    print("\n" + "=" * 52)
    print("   NCAS - NUCLEO COGNITIVO DA AURORA SIGER")
    print("=" * 52)
    print(" 1. Cadastrar alerta operacional")
    print(" 2. Consultar modulos e alertas salvos")
    print(" 3. Analisar alerta operacional")
    print(" 4. Executar validacao logica (tabelas-verdade)")
    print(" 5. Exibir prompts estruturados")
    print(" 6. Simular resposta do assistente")
    print(" 7. Analise de otimizacao de prompt")
    print(" 8. Recarregar dados do JSON")
    print(" 9. Ver logs de acesso")
    print(" 0. Sair")
    print("=" * 52)


def main():
    """Ponto de entrada do sistema."""
    dados = carregar_dados()
    abrir_sessao()
    print(f"\nNucleo Cognitivo iniciado: {len(dados['modulos'])} modulos e "
          f"{len(dados['alertas'])} alertas carregados do disco.")

    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            menu_cadastrar(dados)

        elif opcao == "2":
            listar_modulos(dados)
            listar_alertas(dados)

        elif opcao == "3":
            listar_alertas(dados)
            alerta_id = ler_inteiro("Id do alerta a analisar: ")
            autorizado = ler_sim_nao("Usuario autorizado? (S/N): ")
            analisar_alerta(dados, alerta_id, autorizado)

        elif opcao == "4":
            tabela_verdade()

        elif opcao == "5":
            alerta = pedir_alerta(dados)
            if alerta:
                exibir_prompts(dados, alerta)

        elif opcao == "6":
            alerta = pedir_alerta(dados)
            if alerta:
                for tipo in ("zero_shot", "few_shot", "chain_of_thought", "structured"):
                    print(f"\n[{tipo.upper()}]")
                    print(simular_resposta(dados, alerta, tipo))

        elif opcao == "7":
            alerta = pedir_alerta(dados)
            if alerta:
                comparar_prompts(dados, alerta)

        elif opcao == "8":
            dados = carregar_dados()
            print(f"Dados recarregados de {ARQUIVO_JSON}: "
                  f"{len(dados['modulos'])} modulos, {len(dados['alertas'])} alertas.")
            registrar_log("SISTEMA", "dados recarregados do disco")

        elif opcao == "9":
            exibir_logs(15)

        elif opcao == "0":
            registrar_log("SESSAO", "encerramento do NCAS")
            print("\nEncerrando o Nucleo Cognitivo. Dados persistidos em disco.")
            break

        else:
            print("Opcao invalida. Digite um numero de 0 a 9.")


if __name__ == "__main__":
    main()                  # alerta inexistente

