"""
llm.py - cliente da API do Gemini
chave em variável de ambiente ou arquivo .env.

Oferece executar_agente(): um laço de "function calling" em que o modelo pode pedir para o
nosso código executar ferramentas (somente as liberadas ao agente) e depois escreve a resposta.
Se a chave não existir ou a API falhar, levanta LLMIndisponivel e o chamador usa o fluxo simulado.
"""
import json
import os
import urllib.error
import urllib.request

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
CAMINHO_ENV = os.path.join(PASTA, ".env")
MODELO = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")   
URL = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % MODELO
MAX_VOLTAS = 5      # limite de idas e vindas modelo <-> ferramentas 
TIMEOUT = 40        # segundos


class LLMIndisponivel(Exception):
    """Sem chave, sem rede ou erro da API: o sistema cai para o fluxo simulado."""


def carregar_env():
    """Lê GEMINI_API_KEY de um arquivo .env simples (CHAVE=valor), sem sobrescrever o ambiente."""
    try:
        with open(CAMINHO_ENV, encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    chave, valor = linha.split("=", 1)
                    os.environ.setdefault(chave.strip(), valor.strip().strip('"'))
    except FileNotFoundError:
        pass


def obter_chave():
    carregar_env()
    return os.environ.get("GEMINI_API_KEY", "")


def garantir_chave_api():
    """Devolve True se há chave (variável de ambiente ou .env). Sem chave, avisa e usa o modo simulado."""
    if obter_chave():
        return True
    print("\n  Nenhuma GEMINI_API_KEY encontrada: crie o arquivo .env (modelo em .env.example).")
    print("  Usando o modo simulado.")
    return False


def _chamar_api(corpo):
    """Uma requisição HTTP à API. A chave vai no cabeçalho (não aparece em URL/logs)."""
    chave = obter_chave()
    if not chave:
        raise LLMIndisponivel("GEMINI_API_KEY não configurada")
    requisicao = urllib.request.Request(
        URL, data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": chave})
    try:
        with urllib.request.urlopen(requisicao, timeout=TIMEOUT) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        raise LLMIndisponivel("API respondeu HTTP %s" % erro.code)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as erro:
        raise LLMIndisponivel("falha de rede/resposta: %s" % erro)


def executar_agente(nome, instrucao, mensagem, ferramentas, registrar, chamar=None):
    """Roda UM agente.
      nome        : nome para o tracing
      instrucao   : papel do agente (system prompt)
      mensagem    : o que o agente recebe (pedido e/ou resultado do agente anterior)
      ferramentas : dict  nome -> {"funcao": callable, "declaracao": {...schema...}}  (allowlist)
      registrar   : função de tracing(agente, texto)
      chamar      : função que faz a requisição (padrão: _chamar_api; trocável em testes)
    Devolve o texto final do modelo."""
    chamar = chamar or _chamar_api
    conteudo = [{"role": "user", "parts": [{"text": mensagem}]}]
    corpo = {
        "system_instruction": {"parts": [{"text": instrucao}]},
        "generationConfig": {"temperature": 0.2},
    }
    if ferramentas:
        corpo["tools"] = [{"function_declarations": [f["declaracao"] for f in ferramentas.values()]}]

    for _ in range(MAX_VOLTAS):
        corpo["contents"] = conteudo
        resposta = chamar(corpo)
        try:
            partes = resposta["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError, TypeError):
            raise LLMIndisponivel("resposta sem conteúdo (possível bloqueio de segurança)")
        chamadas = [p["functionCall"] for p in partes if "functionCall" in p]
        if not chamadas:
            texto = "".join(p.get("text", "") for p in partes).strip()
            if not texto:
                raise LLMIndisponivel("resposta vazia")
            return texto
        # o modelo pediu ferramentas: guardamos o turno dele como veio e devolvemos os resultados
        conteudo.append(resposta["candidates"][0]["content"])
        resultados = []
        for chamada in chamadas:
            ferramenta = ferramentas.get(chamada.get("name"))
            if ferramenta is None:
                saida = {"erro": "ferramenta não permitida para este agente"}
                registrar("Guardrail", "%s tentou ferramenta não liberada: %s" % (nome, chamada.get("name")))
            else:
                try:
                    saida = ferramenta["funcao"](**(chamada.get("args") or {}))
                    registrar(nome, "ferramenta %s(%s)" % (chamada["name"], chamada.get("args") or {}))
                except (TypeError, ValueError) as erro:
                    saida = {"erro": "argumentos inválidos: %s" % erro}
                    registrar("Guardrail", "argumentos recusados em %s: %s" % (chamada["name"], erro))
            resultados.append({"functionResponse": {"name": chamada["name"], "response": {"resultado": saida}}})
        conteudo.append({"role": "user", "parts": resultados})
    raise LLMIndisponivel("o agente passou do limite de %d voltas" % MAX_VOLTAS)
