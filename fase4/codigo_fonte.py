import heapq
import json
import os
import time
from collections import deque


class Modulo:
    def __init__(self, nome, tipo, consumo_kw=0.0, geracao_kw=0.0,
                 descricao="", status="OPERACIONAL", prioridade_operacional="MEDIA"):
        self.nome = nome
        self.tipo = tipo
        self.consumo_kw = consumo_kw
        self.geracao_kw = geracao_kw
        self.descricao = descricao
        self.status = status
        self.prioridade_operacional = prioridade_operacional

    def balanco_energia(self):
        return self.geracao_kw - self.consumo_kw

    def __repr__(self):
        return f"Modulo({self.nome}, {self.tipo}, status={self.status})"


class GrafoColonia:
    def __init__(self):
        self.modulos = {}
        self.adjacencia = {}

    def adicionar_modulo(self, modulo: Modulo):
        self.modulos[modulo.nome] = modulo
        if modulo.nome not in self.adjacencia:
            self.adjacencia[modulo.nome] = []

    def adicionar_conexao(self, origem, destino, peso):
        if origem not in self.modulos or destino not in self.modulos:
            raise ValueError("Ambos os modulos precisam existir antes da conexao.")
        self.adjacencia[origem].append((destino, peso))
        self.adjacencia[destino].append((origem, peso))

    def remover_conexao(self, origem, destino):
        self.adjacencia[origem] = [
            (v, p) for (v, p) in self.adjacencia[origem] if v != destino
        ]
        self.adjacencia[destino] = [
            (v, p) for (v, p) in self.adjacencia[destino] if v != origem
        ]

    def vizinhos(self, nome):
        return self.adjacencia.get(nome, [])

    def listar_modulos(self):
        return list(self.modulos.keys())

    def bfs(self, origem):
        visitados = {origem}
        fila = deque([origem])
        ordem = []
        distancias_saltos = {origem: 0}

        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for vizinho, _peso in self.vizinhos(atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    distancias_saltos[vizinho] = distancias_saltos[atual] + 1
                    fila.append(vizinho)

        return ordem, distancias_saltos

    def dfs(self, origem):
        visitados = set()
        pilha = [origem]
        ordem = []

        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue
            visitados.add(atual)
            ordem.append(atual)

            for vizinho, _peso in reversed(self.vizinhos(atual)):
                if vizinho not in visitados:
                    pilha.append(vizinho)

        return ordem

    def modulos_alcancaveis(self, origem):
        return set(self.dfs(origem))

    def dijkstra(self, origem, destino=None):
        distancias = {nome: float("inf") for nome in self.modulos}
        distancias[origem] = 0
        anteriores = {nome: None for nome in self.modulos}
        visitados = set()

        heap = [(0, origem)]

        while heap:
            dist_atual, atual = heapq.heappop(heap)

            if atual in visitados:
                continue
            visitados.add(atual)

            if destino is not None and atual == destino:
                break

            for vizinho, peso in self.vizinhos(atual):
                if vizinho in visitados:
                    continue
                nova_dist = dist_atual + peso
                if nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    anteriores[vizinho] = atual
                    heapq.heappush(heap, (nova_dist, vizinho))

        return distancias, anteriores

    def reconstruir_caminho(self, anteriores, origem, destino):
        if anteriores.get(destino) is None and destino != origem:
            return None

        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            if atual == origem:
                break
            atual = anteriores[atual]
        caminho.reverse()

        if caminho[0] != origem:
            return None
        return caminho

    def pontos_de_articulacao(self):
        criticos = []
        todos = self.listar_modulos()

        for candidato in todos:
            restantes = [m for m in todos if m != candidato]
            if not restantes:
                continue

            backup = {m: list(self.adjacencia[m]) for m in todos}
            for m in todos:
                self.adjacencia[m] = [
                    (v, p) for (v, p) in self.adjacencia[m] if v != candidato
                ]

            origem_teste = restantes[0]
            alcancados = set(self._dfs_sem_modulo(origem_teste, candidato))

            self.adjacencia = backup

            if alcancados != set(restantes):
                criticos.append(candidato)

        return criticos

    def _dfs_sem_modulo(self, origem, excluido):
        visitados = set()
        pilha = [origem]
        ordem = []
        while pilha:
            atual = pilha.pop()
            if atual in visitados or atual == excluido:
                continue
            visitados.add(atual)
            ordem.append(atual)
            for vizinho, _peso in self.adjacencia.get(atual, []):
                if vizinho not in visitados and vizinho != excluido:
                    pilha.append(vizinho)
        return ordem

    def exportar_json(self, caminho_arquivo):
        dados = {
            "modulos": [
                {
                    "nome": m.nome,
                    "tipo": m.tipo,
                    "consumo_kw": m.consumo_kw,
                    "geracao_kw": m.geracao_kw,
                    "status": m.status,
                    "prioridade_operacional": m.prioridade_operacional,
                    "descricao": m.descricao,
                }
                for m in self.modulos.values()
            ],
            "conexoes": self._listar_conexoes_unicas(),
        }
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def _listar_conexoes_unicas(self):
        vistas = set()
        conexoes = []
        for origem, vizinhos in self.adjacencia.items():
            for destino, peso in vizinhos:
                chave = tuple(sorted([origem, destino]))
                if chave not in vistas:
                    vistas.add(chave)
                    conexoes.append({"origem": origem, "destino": destino, "peso": peso})
        return conexoes


def construir_rede_aurora_siger():
    grafo = GrafoColonia()

    modulos = [
        Modulo("Nucleo Energetico", "Geracao de Energia",
               consumo_kw=40, geracao_kw=500,
               descricao="Reator compacto que fornece a maior parte da energia da colonia.",
               prioridade_operacional="CRITICA"),
        Modulo("Campo Solar Norte", "Geracao de Energia",
               consumo_kw=5, geracao_kw=150,
               descricao="Painéis solares na regiao norte da base.",
               prioridade_operacional="ALTA"),
        Modulo("Campo Solar Sul", "Geracao de Energia",
               consumo_kw=5, geracao_kw=140,
               descricao="Painéis solares na regiao sul da base.",
               prioridade_operacional="ALTA"),
        Modulo("Estacao de Armazenamento", "Armazenamento de Energia",
               consumo_kw=10, geracao_kw=0,
               descricao="Baterias de longa duracao para picos de consumo e noites marcianas.",
               prioridade_operacional="CRITICA"),
        Modulo("Suporte a Vida Central", "Suporte a Vida",
               consumo_kw=80, geracao_kw=0,
               descricao="Controle de oxigenio, agua e atmosfera para toda a colonia.",
               prioridade_operacional="CRITICA"),
        Modulo("Habitat A", "Habitat",
               consumo_kw=60, geracao_kw=0,
               descricao="Modulo residencial - ala A.",
               prioridade_operacional="ALTA"),
        Modulo("Habitat B", "Habitat",
               consumo_kw=55, geracao_kw=0,
               descricao="Modulo residencial - ala B.",
               prioridade_operacional="ALTA"),
        Modulo("Habitat C", "Habitat",
               consumo_kw=50, geracao_kw=0,
               descricao="Modulo residencial - ala C.",
               prioridade_operacional="ALTA"),
        Modulo("Estufa Hidroponica", "Producao de Alimento",
               consumo_kw=45, geracao_kw=0,
               descricao="Producao de alimentos via cultivo hidroponico.",
               prioridade_operacional="ALTA"),
        Modulo("Laboratorio de Pesquisa", "Pesquisa",
               consumo_kw=35, geracao_kw=0,
               descricao="Pesquisas cientificas e analises de solo/atmosfera.",
               prioridade_operacional="MEDIA"),
        Modulo("Centro de Comando", "Operacional",
               consumo_kw=25, geracao_kw=0,
               descricao="Controle administrativo e operacional da colonia.",
               prioridade_operacional="CRITICA"),
        Modulo("Reciclagem de Agua", "Suporte a Vida",
               consumo_kw=20, geracao_kw=0,
               descricao="Tratamento e reciclagem de agua da colonia.",
               prioridade_operacional="ALTA"),
        Modulo("Hangar de Veiculos", "Operacional",
               consumo_kw=15, geracao_kw=0,
               descricao="Armazenamento e manutencao de veiculos de superficie.",
               prioridade_operacional="MEDIA"),
    ]

    for m in modulos:
        grafo.adicionar_modulo(m)

    conexoes = [
        ("Nucleo Energetico", "Estacao de Armazenamento", 60),
        ("Nucleo Energetico", "Centro de Comando", 110),
        ("Nucleo Energetico", "Campo Solar Norte", 200),
        ("Nucleo Energetico", "Campo Solar Sul", 210),
        ("Estacao de Armazenamento", "Suporte a Vida Central", 90),
        ("Estacao de Armazenamento", "Habitat A", 130),
        ("Centro de Comando", "Habitat A", 70),
        ("Centro de Comando", "Habitat B", 85),
        ("Centro de Comando", "Laboratorio de Pesquisa", 100),
        ("Habitat A", "Habitat B", 40),
        ("Habitat B", "Habitat C", 45),
        ("Habitat A", "Suporte a Vida Central", 95),
        ("Suporte a Vida Central", "Reciclagem de Agua", 55),
        ("Suporte a Vida Central", "Estufa Hidroponica", 120),
        ("Reciclagem de Agua", "Estufa Hidroponica", 65),
        ("Habitat C", "Estufa Hidroponica", 100),
        ("Laboratorio de Pesquisa", "Estufa Hidroponica", 150),
        ("Centro de Comando", "Hangar de Veiculos", 180),
        ("Campo Solar Norte", "Hangar de Veiculos", 220),
        ("Habitat B", "Laboratorio de Pesquisa", 90),
    ]

    for origem, destino, peso in conexoes:
        grafo.adicionar_conexao(origem, destino, peso)

    return grafo


def simular_falha_modulo(grafo, nome_modulo):
    if nome_modulo not in grafo.modulos:
        return {"erro": f"Modulo '{nome_modulo}' nao existe na rede."}

    conexoes_originais = list(grafo.adjacencia[nome_modulo])
    status_original = grafo.modulos[nome_modulo].status

    grafo.modulos[nome_modulo].status = "INATIVO"
    for vizinho, _peso in conexoes_originais:
        grafo.remover_conexao(nome_modulo, vizinho)

    referencia = "Centro de Comando" if nome_modulo != "Centro de Comando" else "Habitat A"
    alcancaveis = grafo.modulos_alcancaveis(referencia) if referencia in grafo.modulos else set()
    isolados = [m for m in grafo.listar_modulos()
                if m not in alcancaveis and m != nome_modulo]

    relatorio = {
        "modulo_em_falha": nome_modulo,
        "conexoes_perdidas": conexoes_originais,
        "modulos_isolados": isolados,
        "referencia_usada": referencia,
    }

    grafo.modulos[nome_modulo].status = status_original
    grafo.adjacencia[nome_modulo] = []
    for vizinho, peso in conexoes_originais:
        grafo.adjacencia[vizinho] = [(v, p) for (v, p) in grafo.adjacencia[vizinho] if v != nome_modulo]
        grafo.adjacencia[nome_modulo].append((vizinho, peso))
        grafo.adjacencia[vizinho].append((nome_modulo, peso))

    return relatorio


def simular_pico_consumo(grafo, fator=1.5):
    geracao_total = sum(m.geracao_kw for m in grafo.modulos.values())
    consumo_total = sum(m.consumo_kw for m in grafo.modulos.values())
    consumo_simulado_total = consumo_total * fator
    saldo = geracao_total - consumo_simulado_total

    fator_critico = (geracao_total / consumo_total) if consumo_total > 0 else float("inf")

    detalhes = [
        {
            "modulo": m.nome,
            "consumo_normal_kw": m.consumo_kw,
            "consumo_simulado_kw": round(m.consumo_kw * fator, 1),
        }
        for m in grafo.modulos.values()
    ]

    return {
        "fator_pico": fator,
        "geracao_total_kw": geracao_total,
        "consumo_simulado_total_kw": round(consumo_simulado_total, 1),
        "saldo_kw": round(saldo, 1),
        "fator_critico": round(fator_critico, 2),
        "detalhes": detalhes,
    }


def balanco_energetico_geral(grafo):
    geracao_total = sum(m.geracao_kw for m in grafo.modulos.values())
    consumo_total = sum(m.consumo_kw for m in grafo.modulos.values())
    saldo = geracao_total - consumo_total

    if saldo > 0:
        status = "SUPERAVIT"
    elif saldo == 0:
        status = "EQUILIBRIO"
    else:
        status = "DEFICIT"

    return {
        "geracao_total_kw": geracao_total,
        "consumo_total_kw": consumo_total,
        "saldo_kw": saldo,
        "status": status,
    }


LINHA = "-" * 70


def pausar():
    input("\nPressione ENTER para continuar...")


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def cabecalho(titulo):
    limpar_tela()
    print("=" * 70)
    print(f" SIGIC - Aurora Siger | {titulo}")
    print("=" * 70)


def menu_visualizar_rede(grafo):
    cabecalho("Visualizar Rede da Colonia")
    print(f"Total de modulos: {len(grafo.modulos)}")
    print(f"Total de conexoes: {len(grafo._listar_conexoes_unicas())}\n")

    for nome in grafo.listar_modulos():
        modulo = grafo.modulos[nome]
        vizinhos = grafo.vizinhos(nome)
        nomes_vizinhos = ", ".join(f"{v} ({p}m)" for v, p in vizinhos) or "Nenhuma conexao"
        print(f"[{modulo.status:^11}] {nome} ({modulo.tipo})")
        print(f"    Conectado a: {nomes_vizinhos}")
    pausar()


def menu_consultar_modulo(grafo):
    cabecalho("Consultar Modulo")
    print("Modulos disponiveis:")
    for i, nome in enumerate(grafo.listar_modulos(), start=1):
        print(f"  {i}. {nome}")

    escolha = input("\nDigite o nome (ou numero) do modulo: ").strip()

    nomes = grafo.listar_modulos()
    if escolha.isdigit() and 1 <= int(escolha) <= len(nomes):
        nome_modulo = nomes[int(escolha) - 1]
    else:
        nome_modulo = escolha

    modulo = grafo.modulos.get(nome_modulo)
    if not modulo:
        print(f"\nModulo '{escolha}' nao encontrado na rede.")
        pausar()
        return

    print(f"\nNome: {modulo.nome}")
    print(f"Tipo: {modulo.tipo}")
    print(f"Status: {modulo.status}")
    print(f"Prioridade operacional: {modulo.prioridade_operacional}")
    print(f"Consumo: {modulo.consumo_kw} kW")
    print(f"Geracao: {modulo.geracao_kw} kW")
    print(f"Balanco proprio: {modulo.balanco_energia():+.1f} kW")
    print(f"Descricao: {modulo.descricao}")
    vizinhos = grafo.vizinhos(modulo.nome)
    print(f"Conexoes diretas: {len(vizinhos)}")
    for v, p in vizinhos:
        print(f"   -> {v} (distancia: {p}m)")
    pausar()


def menu_caminho_minimo(grafo):
    cabecalho("Caminho Minimo (Dijkstra)")
    nomes = grafo.listar_modulos()
    for i, nome in enumerate(nomes, start=1):
        print(f"  {i}. {nome}")

    origem = input("\nModulo de ORIGEM (nome ou numero): ").strip()
    destino = input("Modulo de DESTINO (nome ou numero): ").strip()

    def resolver(valor):
        if valor.isdigit() and 1 <= int(valor) <= len(nomes):
            return nomes[int(valor) - 1]
        return valor

    origem, destino = resolver(origem), resolver(destino)

    if origem not in grafo.modulos or destino not in grafo.modulos:
        print("\nOrigem ou destino invalidos.")
        pausar()
        return

    distancias, anteriores = grafo.dijkstra(origem, destino)
    caminho = grafo.reconstruir_caminho(anteriores, origem, destino)

    print(f"\nOrigem: {origem}")
    print(f"Destino: {destino}")

    if caminho is None:
        print("\nNao existe caminho entre os modulos selecionados "
              "(rede desconectada nesse trecho).")
    else:
        print(f"\nCaminho minimo encontrado ({len(caminho)} modulos):")
        print("   " + " -> ".join(caminho))
        print(f"\nCusto total (distancia / perda estimada): {distancias[destino]} metros")
    pausar()


def menu_exploracao_bfs_dfs(grafo):
    cabecalho("Exploracao da Rede (BFS / DFS)")
    nomes = grafo.listar_modulos()
    for i, nome in enumerate(nomes, start=1):
        print(f"  {i}. {nome}")

    origem = input("\nModulo de origem para a exploracao: ").strip()
    if origem.isdigit() and 1 <= int(origem) <= len(nomes):
        origem = nomes[int(origem) - 1]

    if origem not in grafo.modulos:
        print("\nModulo invalido.")
        pausar()
        return

    ordem_bfs, saltos = grafo.bfs(origem)
    ordem_dfs = grafo.dfs(origem)
    alcancaveis = grafo.modulos_alcancaveis(origem)
    todos = set(grafo.listar_modulos())
    nao_alcancaveis = todos - alcancaveis

    print(f"\n--- BFS (busca em largura) a partir de '{origem}' ---")
    print("Ordem de visita:", " -> ".join(ordem_bfs))
    print("\nNumero minimo de saltos (conexoes) até cada modulo:")
    for nome, dist in sorted(saltos.items(), key=lambda x: x[1]):
        print(f"   {nome}: {dist} salto(s)")

    print(f"\n--- DFS (busca em profundidade) a partir de '{origem}' ---")
    print("Ordem de visita:", " -> ".join(ordem_dfs))

    print(f"\nModulos alcancaveis a partir de '{origem}': {len(alcancaveis)}/{len(todos)}")
    if nao_alcancaveis:
        print("Modulos NAO alcancaveis (rede desconectada):", ", ".join(nao_alcancaveis))
    else:
        print("A rede esta totalmente conectada a partir deste modulo.")
    pausar()


def menu_pontos_criticos(grafo):
    cabecalho("Modulos Criticos da Rede (Pontos de Articulacao)")
    print("Calculando... isso identifica modulos cuja falha isola partes da colonia.\n")
    criticos = grafo.pontos_de_articulacao()
    if criticos:
        print("Modulos CRITICOS encontrados:")
        for c in criticos:
            print(f"   - {c}")
        print("\nRecomendacao de governanca: priorizar redundancia "
              "(conexoes alternativas) nesses pontos.")
    else:
        print("Nenhum ponto critico encontrado: a rede tem boa redundancia.")
    pausar()


def menu_simulacoes(grafo):
    while True:
        cabecalho("Simulacoes Operacionais")
        print("1. Simular falha de um modulo (analise de impacto)")
        print("2. Simular pico de consumo energetico")
        print("3. Ver balanco energetico atual da colonia")
        print("0. Voltar ao menu principal")
        opcao = input("\nEscolha uma opcao: ").strip()

        if opcao == "1":
            cabecalho("Simulacao: Falha de Modulo")
            nomes = grafo.listar_modulos()
            for i, nome in enumerate(nomes, start=1):
                print(f"  {i}. {nome}")
            escolha = input("\nQual modulo vai falhar? (nome ou numero): ").strip()
            if escolha.isdigit() and 1 <= int(escolha) <= len(nomes):
                escolha = nomes[int(escolha) - 1]

            relatorio = simular_falha_modulo(grafo, escolha)
            if "erro" in relatorio:
                print(f"\n{relatorio['erro']}")
            else:
                print(f"\nSimulando falha em: {relatorio['modulo_em_falha']}")
                print(f"Conexoes perdidas: {len(relatorio['conexoes_perdidas'])}")
                if relatorio["modulos_isolados"]:
                    print("Modulos que ficariam ISOLADOS da colonia:")
                    for m in relatorio["modulos_isolados"]:
                        print(f"   - {m}")
                else:
                    print("Nenhum modulo ficaria isolado (rede resiliente a esta falha).")
                print("\n(Simulacao nao-destrutiva: a rede foi restaurada automaticamente.)")
            pausar()

        elif opcao == "2":
            cabecalho("Simulacao: Pico de Consumo")
            fator_str = input("Fator multiplicador do consumo (ex: 1.5 para +50%): ").strip()
            try:
                fator = float(fator_str.replace(",", "."))
            except ValueError:
                fator = 1.5
                print("Valor invalido, usando fator padrao 1.5.")

            relatorio = simular_pico_consumo(grafo, fator)
            print(f"\nFator de pico aplicado: {relatorio['fator_pico']}x")
            print(f"Geracao total da colonia: {relatorio['geracao_total_kw']} kW")
            print(f"Consumo simulado total:  {relatorio['consumo_simulado_total_kw']} kW")
            saldo = relatorio["saldo_kw"]
            if saldo >= 0:
                print(f"Saldo energetico: +{saldo} kW (colonia suporta o pico).")
            else:
                print(f"Saldo energetico: {saldo} kW (DEFICIT! risco operacional).")
            print(f"Fator critico (ponto de deficit): {relatorio['fator_critico']}x "
                  "(acima deste fator a colonia entra em deficit energetico).")
            pausar()

        elif opcao == "3":
            cabecalho("Balanco Energetico Atual")
            b = balanco_energetico_geral(grafo)
            print(f"Geracao total: {b['geracao_total_kw']} kW")
            print(f"Consumo total: {b['consumo_total_kw']} kW")
            print(f"Saldo: {b['saldo_kw']:+.1f} kW")
            print(f"Status energetico: {b['status']}")
            pausar()

        elif opcao == "0":
            break
        else:
            print("\nOpcao invalida.")
            time.sleep(1)


def menu_exportar(grafo):
    cabecalho("Exportar Dados da Rede")
    pasta = "arquivos_auxiliares"
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "rede_colonia_export.json")
    grafo.exportar_json(caminho)
    print(f"Dados da rede exportados com sucesso para: {caminho}")
    pausar()


def menu_principal():
    grafo = construir_rede_aurora_siger()

    while True:
        cabecalho("Menu Principal")
        print("Bem-vindo ao SIGIC - Sistema Inteligente de Gerenciamento")
        print("da Infraestrutura da Colonia Aurora Siger.\n")
        print("1. Visualizar rede da colonia")
        print("2. Consultar modulo especifico")
        print("3. Calcular caminho minimo entre modulos (Dijkstra)")
        print("4. Explorar conectividade da rede (BFS / DFS)")
        print("5. Identificar modulos criticos da rede")
        print("6. Simulacoes operacionais (falhas / picos de consumo)")
        print("7. Exportar dados da rede (arquivo auxiliar .json)")
        print("0. Sair do sistema")
        print(LINHA)

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            menu_visualizar_rede(grafo)
        elif opcao == "2":
            menu_consultar_modulo(grafo)
        elif opcao == "3":
            menu_caminho_minimo(grafo)
        elif opcao == "4":
            menu_exploracao_bfs_dfs(grafo)
        elif opcao == "5":
            menu_pontos_criticos(grafo)
        elif opcao == "6":
            menu_simulacoes(grafo)
        elif opcao == "7":
            menu_exportar(grafo)
        elif opcao == "0":
            cabecalho("Encerrando o SIGIC")
            print("Encerrando o sistema. Ate a proxima, comandante!\n")
            break
        else:
            print("\nOpcao invalida, tente novamente.")
            time.sleep(1)


def main():
    menu_principal()


if __name__ == "__main__":
    main()
