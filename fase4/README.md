# Fase 4 - SIGIC: Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia

Sistema desenvolvido para representar computacionalmente a infraestrutura da colônia
marciana **Aurora Siger** e otimizar o funcionamento da sua rede energética e
operacional, utilizando grafos, algoritmos de caminhos mínimos e estruturas de
dados em Python puro.

## Descrição do projeto

A colônia Aurora Siger é modelada como um **grafo ponderado e não-direcionado**,
onde cada módulo da infraestrutura (geração de energia, suporte à vida, habitats,
produção de alimento, pesquisa e operações) é um vértice, e as conexões físicas
entre eles (dutos de energia/túneis) são arestas com peso (distância em metros,
usada como proxy de perda de energia).

A rede modelada possui 13 módulos e 20 conexões:

- **Geração/armazenamento de energia**: Núcleo Energético, Campo Solar Norte,
  Campo Solar Sul, Estação de Armazenamento
- **Suporte à vida**: Suporte à Vida Central, Reciclagem de Água
- **Habitats**: Habitat A, Habitat B, Habitat C
- **Produção de alimento**: Estufa Hidropônica
- **Pesquisa e operação**: Laboratório de Pesquisa, Centro de Comando, Hangar de
  Veículos

Cada módulo possui, além do consumo e geração de energia, uma **prioridade
operacional** (CRITICA, ALTA ou MEDIA), usada como critério de governança para
priorizar investimentos em redundância e resposta a falhas.

## Conteúdo da pasta

| Arquivo | Descrição |
|---|---|
| `Main.py` | Arquivo principal do sistema (executável via terminal) |
| `rede_colonia.pdf` | Diagrama visual da rede/grafo da colônia |
| `documentacao_complementar.pdf` | Documentação com infraestrutura, algoritmos, estruturas de dados, modelagem matemática (incluindo cálculo diferencial aplicado) e reflexão ESG |
| `link_video.txt` | Link do vídeo de apresentação (YouTube, não listado) |
| `arquivos_auxiliares/` | Dados de apoio (export JSON da rede) |

## Funcionalidades implementadas

O sistema roda por um menu de navegação no terminal e permite:

1. Visualizar a rede da colônia (módulos, conexões e status)
2. Consultar informações detalhadas de um módulo específico (incluindo
   **prioridade operacional**: CRITICA, ALTA ou MEDIA)
3. Calcular o caminho mínimo entre dois módulos (algoritmo de **Dijkstra**)
4. Explorar a conectividade da rede via **BFS** (busca em largura) e **DFS**
   (busca em profundidade)
5. Identificar módulos críticos da rede (pontos de articulação, cuja falha
   isolaria parte da colônia)
6. Simular situações operacionais:
   - Falha de um módulo (análise de impacto na conectividade)
   - Pico de consumo energético (cálculo de déficit/superávit e do
     **fator crítico**: o multiplicador de consumo a partir do qual a
     colônia entra em déficit energético)
   - Balanço energético geral da colônia, com **status interpretado**
     automaticamente (SUPERAVIT, EQUILIBRIO ou DEFICIT)
7. Exportar os dados da rede para um arquivo `.json` auxiliar

## Algoritmos utilizados

- **Dijkstra** (com heap binário via `heapq`) — caminho de menor custo entre
  módulos, complexidade O((V + E) log V)
- **BFS** (com `deque`) — menor número de saltos entre módulos, O(V + E)
- **DFS** (iterativo, com pilha) — verificação de conectividade geral, O(V + E)
- **Pontos de articulação** — identificação de módulos críticos cuja remoção
  desconecta a rede

## Estruturas de dados utilizadas

- `dict` — lista de adjacência do grafo (acesso O(1) aos vizinhos)
- `list` / `tuple` — vizinhos e arestas (`(módulo, peso)`)
- `set` — controle de nós visitados em BFS/DFS
- `heapq` — fila de prioridade do Dijkstra
- `deque` — fila da busca em largura
- `class` — encapsulamento dos atributos de cada módulo (`Modulo`), incluindo
  consumo, geração, status e prioridade operacional

## Modelagem matemática

Além do balanço energético geral (Saldo = ΣG(v) − ΣC(v)), o sistema modela o
comportamento do saldo em função do fator de pico de consumo `f`:

Saldo(f) = ΣG(v) − f · ΣC(v)

A derivada dessa função em relação a `f` (dSaldo/df = −ΣC(v)) representa a taxa
de queda do saldo energético por unidade de aumento no fator de pico — ou seja,
o quanto a colônia perde de margem energética a cada acréscimo no consumo
simulado. A partir dessa relação linear, o sistema calcula o **fator crítico**
(f* = ΣG(v) / ΣC(v)), o ponto exato em que o saldo se anula e a colônia entra
em déficit. Mais detalhes na seção de modelagem matemática do
`documentacao_complementar.pdf`.

## Sustentabilidade e governança (ESG)

O projeto reflete sobre os três pilares ESG aplicados à infraestrutura da colônia:

- **Ambiental**: combinação de geração nuclear compacta com energia solar
  complementar, armazenamento de excedente em baterias, reciclagem de água e
  produção própria de alimentos.
- **Social**: distribuição equitativa de energia/água/oxigênio entre os
  habitats, com redundância de rotas aumentando a resiliência para a tripulação.
- **Governança**: uso de algoritmos de grafos (pontos de articulação e
  simulações de pico de consumo) como ferramenta objetiva de priorização de
  investimentos em redundância e prevenção de falhas, agora reforçada pela
  prioridade operacional de cada módulo.

## Como executar

Requer apenas Python 3 (biblioteca padrão, sem dependências externas):

```bash
python Main.py
```

Navegue pelo menu digitando o número da opção desejada.

## Regras técnicas

O sistema utiliza exclusivamente bibliotecas padrão do Python (`heapq`, `json`,
`os`, `time`, `collections`), sem frameworks externos como `networkx` ou
`matplotlib`.
