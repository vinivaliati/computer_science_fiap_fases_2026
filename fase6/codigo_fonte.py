# SCIC - Sistema de Comunicacao Inteligente da Colonia
# Missao Aurora Siger

# Sistema em terminal para organizar, analisar e priorizar dados de
# comunicacao da colonia. Dados simulados, sem hardware ou APIs reais.

import os
import math
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

CAMINHO_DADOS = "dados_aurora_siger.csv"
COLUNAS = [
    "id_alerta", "modulo", "codigo_sensor_hex", "codigo_sensor_dec",
    "status", "criticidade", "latencia_prevista_ms", "latencia_real_ms",
    "tensao_v", "corrente_a", "tempo_desde_registro_min", "risco_operacional",
]


def com_metricas(df):
    # calcula as colunas derivadas usadas em varias telas do menu (erro, potencia etc).
    # feito com operacoes vetorizadas do pandas/numpy, sem loop linha a linha.
    df2 = df.copy()
    df2["atraso_ms"] = (df2["latencia_real_ms"] - df2["latencia_prevista_ms"]).round(3)
    df2["erro_absoluto_ms"] = df2["atraso_ms"].abs().round(3)
    df2["erro_relativo_pct"] = np.where(
        df2["latencia_real_ms"] != 0,
        df2["erro_absoluto_ms"] / df2["latencia_real_ms"] * 100,
        0.0,
    ).round(2)
    df2["potencia_w"] = (df2["tensao_v"] * df2["corrente_a"]).round(3)
    return df2


def carregar_dados(caminho=CAMINHO_DADOS):
    if not os.path.exists(caminho):
        print(f"\nArquivo '{caminho}' nao encontrado. Iniciando com base vazia.\n")
        return pd.DataFrame(columns=COLUNAS)

    df = pd.read_csv(caminho)
    print(f"\n{len(df)} registros carregados de '{caminho}'.\n")
    return df


def classificar_status(criticidade, atraso):
    if criticidade >= 4 or atraso > 15:
        return "Critico"
    if criticidade == 3 or atraso > 5:
        return "Atencao"
    return "Normal"


def cadastrar_novo_registro(df):
    print("\n--- Cadastro de novo registro ---")
    try:
        codigo_dec = int(input("Codigo do sensor (decimal, 0-255): "))
        latencia_prevista = float(input("Latencia prevista (ms): "))
        latencia_real = float(input("Latencia real observada (ms): "))
        criticidade = int(input("Criticidade (1 a 5): "))

        registro = {
            "id_alerta": f"AL-{len(df) + 1:03d}",
            "modulo": input("Nome do modulo: ").strip(),
            "codigo_sensor_hex": f"0x{codigo_dec:02X}",
            "codigo_sensor_dec": codigo_dec,
            "criticidade": criticidade,
            "latencia_prevista_ms": latencia_prevista,
            "latencia_real_ms": latencia_real,
            "tensao_v": float(input("Tensao do modulo (V): ")),
            "corrente_a": float(input("Corrente do modulo (A): ")),
            "tempo_desde_registro_min": int(input("Tempo desde o registro (min): ")),
            "risco_operacional": input("Risco operacional (Baixo/Medio/Alto): ").strip().title(),
        }
        registro["status"] = classificar_status(criticidade, latencia_real - latencia_prevista)

        df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
        print(f"\nRegistro '{registro['id_alerta']}' cadastrado. Status: {registro['status']}\n")
    except ValueError:
        print("\nValor invalido. Cadastro cancelado.\n")
    return df


def consultar_registros(df):
    if df.empty:
        print("\nNenhum dado carregado ainda.\n")
        return

    print("\n1. Ver todos  2. Por modulo  3. Por status  4. Por criticidade minima")
    opcao = input("Opcao: ").strip()

    if opcao == "1":
        resultado = df
    elif opcao == "2":
        termo = input("Nome (ou parte do nome) do modulo: ").strip()
        resultado = df[df["modulo"].str.contains(termo, case=False, na=False)]
    elif opcao == "3":
        termo = input("Status (Normal/Atencao/Critico): ").strip().title()
        resultado = df[df["status"] == termo]
    elif opcao == "4":
        try:
            minimo = int(input("Criticidade minima (1 a 5): "))
            resultado = df[df["criticidade"] >= minimo]
        except ValueError:
            print("Valor invalido.")
            return
    else:
        print("Opcao invalida.")
        return

    print(resultado.to_string(index=False) if not resultado.empty else "Nenhum registro encontrado.")
    print()


def calcular_indicadores_erros(df):
    if df.empty:
        print("\nCarregue os dados primeiro (opcao 1).\n")
        return

    df2 = com_metricas(df)
    colunas = ["id_alerta", "modulo", "latencia_prevista_ms", "latencia_real_ms",
               "erro_absoluto_ms", "erro_relativo_pct", "potencia_w"]
    print("\n" + df2[colunas].to_string(index=False))

    limite = 15.0
    pct_preocupante = (df2["erro_relativo_pct"] > limite).mean() * 100

    print(f"\nErro absoluto medio: {df2['erro_absoluto_ms'].mean():.3f} ms")
    print(f"Erro relativo medio: {df2['erro_relativo_pct'].mean():.2f}%")
    print(f"Potencia media: {df2['potencia_w'].mean():.3f} W")
    print(f"Acima de {limite:.0f}% de erro relativo: {pct_preocupante:.1f}% dos registros")
    print("(erro relativo normaliza pela escala de cada modulo; diferencas residuais")
    print("tambem vem de arredondamento e representacao em ponto flutuante)\n")


def executar_modelo_previsao(df):
    # regressao linear simples: tenta prever a latencia real a partir de
    # atributos operacionais, depois compara com o baseline (latencia_prevista_ms)
    if df.empty or len(df) < 10:
        print("\nSao necessarios pelo menos 10 registros para treinar o modelo.\n")
        return

    atributos = ["criticidade", "tensao_v", "corrente_a", "tempo_desde_registro_min"]
    X = df[atributos]
    y = df["latencia_real_ms"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    modelo = LinearRegression().fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # baseline de comparacao: usar a latencia ja prevista como se fosse a previsao do modelo
    baseline = df.loc[X_test.index, "latencia_prevista_ms"]
    mae_base = mean_absolute_error(y_test, baseline)
    mse_base = mean_squared_error(y_test, baseline)
    rmse_base = math.sqrt(mse_base)

    print(f"\nTreino: {len(X_train)} registros | Teste: {len(X_test)} registros")
    print(f"{'':10}{'Modelo':>12}{'Baseline':>12}")
    print(f"{'MAE':10}{mae:>12.3f}{mae_base:>12.3f}")
    print(f"{'MSE':10}{mse:>12.3f}{mse_base:>12.3f}")
    print(f"{'RMSE':10}{rmse:>12.3f}{rmse_base:>12.3f}")
    print(f"{'R2':10}{r2:>12.3f}")
    print("\n(R2 isolado nao basta para avaliar o modelo: aqui ele deu negativo, ou seja,")
    print("o modelo ficou pior que o baseline, o que so fica claro comparando MAE/RMSE)\n")


class FilaPrioridade:
    # max-heap em vetor, com heapify-up/down escritos manualmente

    def __init__(self):
        self.itens = []

    def vazio(self):
        return not self.itens

    def inserir(self, prioridade, alerta):
        self.itens.append((prioridade, alerta))
        self._subir(len(self.itens) - 1)

    def _subir(self, i):
        while i > 0:
            pai = (i - 1) // 2
            if self.itens[i][0] <= self.itens[pai][0]:
                break
            self.itens[i], self.itens[pai] = self.itens[pai], self.itens[i]
            i = pai

    def extrair_maior(self):
        if self.vazio():
            return None
        topo = self.itens[0]
        ultimo = self.itens.pop()
        if self.itens:
            self.itens[0] = ultimo
            self._descer(0)
        return topo

    def _descer(self, i):
        n = len(self.itens)
        while True:
            esq, dir_ = 2 * i + 1, 2 * i + 2
            maior = i
            if esq < n and self.itens[esq][0] > self.itens[maior][0]:
                maior = esq
            if dir_ < n and self.itens[dir_][0] > self.itens[maior][0]:
                maior = dir_
            if maior == i:
                break
            self.itens[i], self.itens[maior] = self.itens[maior], self.itens[i]
            i = maior


def calcular_prioridades(df):
    # criterio de urgencia do alerta: criticidade pesa mais (x10), depois o
    # atraso de latencia, o risco operacional e por fim o tempo de espera
    # (bonus pequeno para nao deixar alertas antigos esquecidos na fila)
    peso_risco = df["risco_operacional"].map({"Baixo": 0, "Medio": 5, "Alto": 10}).fillna(0)
    atraso = (df["latencia_real_ms"] - df["latencia_prevista_ms"]).clip(lower=0)
    prioridade = df["criticidade"] * 10 + atraso * 0.5 + peso_risco + df["tempo_desde_registro_min"] * 0.05
    return prioridade.round(2)


def priorizar_alertas_heap(df):
    if df.empty:
        print("\nCarregue os dados primeiro (opcao 1).\n")
        return

    try:
        quantidade = int(input("\nQuantos alertas mais urgentes deseja ver? (padrao 5): ") or 5)
    except ValueError:
        quantidade = 5

    prioridades = calcular_prioridades(df)
    fila = FilaPrioridade()
    for prioridade, alerta in zip(prioridades, df.to_dict("records")):
        fila.inserir(prioridade, alerta)

    print(f"\n{'ID':<10}{'Modulo':<26}{'Status':<10}{'Criticidade':<12}{'Prioridade':<10}")
    for _ in range(min(quantidade, len(df))):
        prioridade, alerta = fila.extrair_maior()
        print(f"{alerta['id_alerta']:<10}{alerta['modulo'][:24]:<26}"
              f"{alerta['status']:<10}{alerta['criticidade']:<12}{prioridade:<10}")

    print("\nNuma lista simples, achar o mais urgente custa O(n); no heap, inserir e")
    print("extrair custam O(log n), o que compensa bastante com alertas chegando sempre.\n")


class Trie:
    def __init__(self):
        self.filhos = {}
        self.fim = set()

    def inserir(self, palavra):
        no = self
        for letra in palavra.lower():
            no = no.filhos.setdefault(letra, Trie())
        no.fim.add(palavra.lower())

    def _coletar(self, prefixo, resultados):
        if self.fim:
            resultados.append(prefixo)
        for letra, filho in self.filhos.items():
            filho._coletar(prefixo + letra, resultados)

    def buscar_prefixo(self, prefixo):
        no = self
        prefixo = prefixo.lower()
        for letra in prefixo:
            if letra not in no.filhos:
                return []
            no = no.filhos[letra]
        resultados = []
        no._coletar(prefixo, resultados)
        return sorted(resultados)


def busca_prefixo_trie(df):
    if df.empty:
        print("\nCarregue os dados primeiro (opcao 1).\n")
        return

    print("\n1. Buscar por nome de modulo  2. Buscar por codigo de sensor (hex)")
    opcao = input("Opcao: ").strip()

    if opcao == "1":
        trie = Trie()
        for nome in df["modulo"].unique():
            trie.inserir(nome)
            for palavra in nome.split():
                trie.inserir(palavra)
        prefixo = input("Prefixo do modulo (ex: 'com'): ").strip()
        resultados = trie.buscar_prefixo(prefixo)
        print(resultados if resultados else "Nada encontrado para esse prefixo.")

    elif opcao == "2":
        trie = Trie()
        for codigo in df["codigo_sensor_hex"].unique():
            trie.inserir(codigo.replace("0x", ""))
        prefixo = input("Prefixo do codigo hex (ex: '1'): ").strip()
        resultados = trie.buscar_prefixo(prefixo)
        print([f"0x{r.upper()}" for r in resultados] if resultados else "Nada encontrado para esse prefixo.")
    else:
        print("Opcao invalida.")
        return

    print("Busca por prefixo numa trie custa O(k), k = tamanho do prefixo,")
    print("independente de quantos registros existem na base.\n")


def bases_numericas_eletricidade(df):
    print("\n1. Converter decimal para binario/hex  2. Ver codigo de sensor  3. Potencia (Lei de Ohm)")
    opcao = input("Opcao: ").strip()

    if opcao == "1":
        try:
            valor = int(input("Numero decimal (0-255): "))
            print(f"Binario: {valor:08b}  Hexadecimal: 0x{valor:02X}")
        except ValueError:
            print("Valor invalido.")

    elif opcao == "2":
        if df.empty:
            print("Carregue os dados primeiro (opcao 1).")
            return
        id_busca = input("id_alerta (ex: AL-001): ").strip().upper()
        linha = df[df["id_alerta"] == id_busca]
        if linha.empty:
            print("Registro nao encontrado.")
        else:
            dec = int(linha.iloc[0]["codigo_sensor_dec"])
            print(f"Decimal: {dec}  Binario: {dec:08b}  Hex: {linha.iloc[0]['codigo_sensor_hex']}")

    elif opcao == "3":
        try:
            tensao = float(input("Tensao (V): "))
            corrente = float(input("Corrente (A): "))
            resistencia = tensao / corrente if corrente else float("inf")
            print(f"Potencia (P = V x I): {tensao * corrente:.3f} W")
            print(f"Resistencia (R = V / I): {resistencia:.3f} ohms")
        except ValueError:
            print("Valor invalido.")
    else:
        print("Opcao invalida.")
    print()


def analise_final(df):
    if df.empty:
        print("\nCarregue os dados primeiro (opcao 1).\n")
        return

    df2 = com_metricas(df)
    pct_critico = (df2["status"] == "Critico").mean() * 100
    pct_atencao = (df2["status"] == "Atencao").mean() * 100

    print(f"\nTotal de registros: {len(df2)}")
    print(f"Criticos: {pct_critico:.1f}%   Atencao: {pct_atencao:.1f}%")
    print(f"Erro relativo medio: {df2['erro_relativo_pct'].mean():.2f}%")
    print(f"Potencia media: {df2['potencia_w'].mean():.3f} W")
    print(f"\nCom {pct_critico:.1f}% dos alertas em estado critico, monitoramento continuo")
    print("e manutencao preditiva reduziriam o risco de falha nao detectada. O heap")
    print("prioriza automaticamente o que tratar primeiro, e a trie agiliza achar")
    print("modulos e sensores conforme a base cresce - a base de uma rede de")
    print("comunicacao mais inteligente para a colonia.")
    print("Reflexao social, cultural e de sustentabilidade: ver relatorio_tecnico.md\n")


MENU = """
SCIC - Sistema de Comunicacao Inteligente da Colonia

1. Carregar dados
2. Cadastrar novo registro
3. Consultar registros
4. Indicadores e erros numericos
5. Previsao e avaliacao do modelo
6. Priorizar alertas (heap)
7. Buscar por prefixo (trie)
8. Bases numericas e eletricidade
9. Analise final
0. Sair
"""

ACOES = {
    "4": calcular_indicadores_erros,
    "5": executar_modelo_previsao,
    "6": priorizar_alertas_heap,
    "7": busca_prefixo_trie,
    "8": bases_numericas_eletricidade,
    "9": analise_final,
}


def main():
    df = pd.DataFrame()

    while True:
        print(MENU)
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            df = carregar_dados()
        elif opcao == "2":
            df = cadastrar_novo_registro(df)
        elif opcao == "3":
            consultar_registros(df)
        elif opcao in ACOES:
            ACOES[opcao](df)
        elif opcao == "0":
            print("\nEncerrando o SCIC.\n")
            break
        else:
            print("\nOpcao invalida.\n")


if __name__ == "__main__":
    main()
