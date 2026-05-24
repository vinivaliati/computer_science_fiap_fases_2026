#  Bryan Lima Garcia
#  colonia.py — Dados e estrutura da Colônia Inteligente
# -
#  Responsabilidade: organizar todos os dados da colônia em
#  estruturas de fácil acesso (chave-valor e hierarquia).
# -


def criar_colonia():
    """
    Retorna um dicionário com todos os dados da colônia:
    - dados operacionais (energia, geração, clima)
    - hierarquia de subsistemas
    - histórico para regressão linear
    """
    colonia = {
        # ─ Dados operacionais
        "dados": {
            "energia_reserva_pct": 55,      # nível da bateria (0-100 %)
            "consumo_total_kw":    68,      # consumo atual da colônia

            "geracao_solar_kw":    30,      # geração pelo painel solar
            "geracao_eolica_kw":   25,      # geração pelos aerogeradores

            "clima": {
                "vento_mps":      11,       # velocidade do vento (m/s)
                "temperatura_c": -10        # temperatura ambiente (°C)
            }
        },

        # ─ Hierarquia de subsistemas
        #    energia → solar / eólico / bateria
        #    segurança → câmeras / sensores / travas
        "sistemas": {
            "energia": {
                "solar":   {"ativo": True, "geracao_atual_kw": 30},
                "eolico":  {"ativo": True, "geracao_atual_kw": 25},
                "bateria": {"ativo": True, "nivel_pct":        55}
            },
            "seguranca": {
                "ativo": True,
                "modos": {
                    "cameras":            True,
                    "sensores_perimetro": True,
                    "travas":             True
                }
            }
        },

        # ─ Histórico para regressão (vento → energia eólica) ─
        "historico": {
            "vento_mps":        [8,  10, 12],
            "energia_eolica_kw": [20, 25, 30]
        }
    }
    return colonia


def listar_subsistemas(colonia):
    """
    Percorre a hierarquia de 'sistemas' e devolve uma lista com
    todos os caminhos encontrados.

    Exemplo de saída:
        ['energia', 'energia/solar', 'energia/solar/ativo', ...]
    """
    caminhos = []

    def percorrer(no, prefixo=""):
        if isinstance(no, dict):
            for chave, valor in no.items():
                caminho = f"{prefixo}/{chave}" if prefixo else chave
                caminhos.append(caminho)
                percorrer(valor, caminho)

    percorrer(colonia["sistemas"])
    return caminhos
