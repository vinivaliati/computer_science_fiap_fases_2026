# Aurora Siger — MGCE (Módulo de Gerenciamento da Colônia Espacial)

Simulação de um sistema de gestão energética para a colônia espacial Marte-I, utilizando estruturas de dados, regressão linear e lógica condicional para tomada de decisão automática em um ambiente crítico.

---

## Organização

    fase3/
    ├── main.py              # ponto de entrada do sistema
    ├── src/
    │   ├── dados.py         # estruturas estáticas: hierarquia, prioridades e limiares
    │   ├── decisao.py       # regras de decisão automática
    │   ├── energia.py       # análise de balanço energético
    │   ├── previsao.py      # regressão linear: irradiância → energia gerada
    │   └── relatorio.py     # montagem e impressão do relatório final
    ├── data/
    │   └── gerar.py         # geração dos dados simulados da colônia
    ├── referencias/
    │   ├── instrucoes_fase3.md
    │   └── img/             # imagens de referência e gráficos gerados
    ├── code/                # código individual de cada integrante
    └── relatorio.pdf        # relatório final

---

## O que o sistema faz

- Gera 365 dias de leituras simuladas da colônia (irradiância, energia, temperatura, bateria)
- Organiza os dados em estruturas de dicionário e hierarquia de sistemas
- Analisa o balanço energético diário e classifica cada dia como:
  - DEFICIT
  - EQUILIBRADO
  - EXCEDENTE
- Aplica regras de decisão automática com base nas condições da colônia
- Classifica cada dia por status de decisão:
  - EMERGENCIA
  - ALERTA
  - AVISO
  - NORMAL
- Treina um modelo de regressão linear com os dados gerados
- Prevê a energia gerada a partir de um valor de irradiância solar
- Exibe um resumo anual e o detalhe de um dia sorteado aleatoriamente

---

## Regras de Decisão

| Condição | Ação |
|---|---|
| Bateria < 20% | EMERGENCIA: desligar sistemas não essenciais |
| Bateria < 40% e consumo alto | ALERTA: ativar modo economia |
| Bateria < 40% | AVISO: monitorar consumo |
| Geração < 35 kWh | AVISO: verificar painéis solares |
| Temp interna fora de 18–28°C | ALERTA: acionar aquecimento/resfriamento |

Sistemas são desligados em ordem inversa de prioridade:
`suporte_vida (1) > comunicacao (2) > laboratorio (3) > navegacao (4)`

---

## Estruturas Utilizadas

- Dicionário → estado atual da colônia e hierarquia de sistemas
- Listas → histórico de registros diários
- Condicionais (if/elif/else) → lógica de decisão automática
- Regressão linear (mínimos quadrados) → previsão de energia gerada

---

## Modelagem Matemática

O sistema aplica regressão linear simples por mínimos quadrados para relacionar a irradiância solar (W/m²) com a energia gerada (kWh) pelos painéis fotovoltaicos:

    energia = a × irradiância + b

Os coeficientes `a` e `b` são calculados a partir dos 365 dias gerados, sem uso de bibliotecas externas.

---

## Como rodar

1. Clone o repositório

        git clone https://github.com/vinivaliati/computer_science_fiap/tree/main/fase3
        cd seu-repositorio/fase3

2. Crie e ative o ambiente virtual

        # Windows
        python -m venv venv
        venv\Scripts\activate

        # Mac/Linux
        python -m venv venv
        source venv/bin/activate

3. Instale as dependências

        pip install matplotlib

4. Execute o sistema

        python main.py

   Para gerar os gráficos:

        python graficos.py

---

## Dependências

    random       # geração dos dados simulados (stdlib)
    math         # cálculos da regressão (stdlib)
    matplotlib   # geração dos gráficos (apenas graficos.py)

---

## Observação

Este projeto foi desenvolvido com foco educacional, aplicando conceitos de estruturas de dados, lógica condicional e modelagem matemática para simular um sistema inteligente de gestão energética em um cenário espacial crítico.