def criar_colonia():
    colonia = {
        "dados": {
            # Energia
            "energia_reserva_pct": 55,   # 0..100 (nível da bateria)
            "consumo_total_kw": 68,

            # Geração atual (por fonte)
            "geracao_solar_kw": 30,
            "geracao_eolica_kw": 25,

            # Clima / ambiente
            "clima": {
                "vento_mps": 11,
                "temperatura_c": -10
            }
        },

        # Hierarquia de subsistemas
        "sistemas": {
            "energia": {
                "solar":   {"ativo": True, "geracao_atual_kw": 30},
                "eolico":  {"ativo": True, "geracao_atual_kw": 25},
                "bateria": {"ativo": True, "nivel_pct": 55}
            },
            "seguranca": {
                "ativo": True,
                "modos": {
                    "cameras": True,
                    "sensores_perimetro": True,
                    "travas": True
                }
            }
        },

        # Histórico para regressão (vento -> energia eólica)
        "historico": {
            "vento_mps": [8, 10, 12],
            "energia_eolica_kw": [20, 25, 30]
        }
    }
    return colonia


def listar_subsistemas(colonia):
    caminhos = []

    def percorrer(no, prefixo=""):
        if isinstance(no, dict):
            for chave, valor in no.items():
                novo = f"{prefixo}/{chave}" if prefixo else chave
                caminhos.append(novo)
                percorrer(valor, novo)

    percorrer(colonia["sistemas"])
    return caminhos
