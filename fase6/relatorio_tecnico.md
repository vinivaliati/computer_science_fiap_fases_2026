# Relatório Técnico — SCIC (Sistema de Comunicação Inteligente da Colônia)
## Missão Aurora Siger

## 1. Contexto da solução

A Aurora Siger é uma colônia simulada em Marte que depende de comunicação constante
entre seus módulos (comunicação, navegação, suporte vital, energia, sensoriamento,
hidroponia e segurança). O **SCIC** foi desenvolvido para organizar os dados simulados
dessa colônia, calcular indicadores de desempenho, priorizar alertas críticos e permitir
buscas rápidas por módulos e sensores, aplicando os conteúdos estudados até esta fase
(Python, Pandas/NumPy, análise de erro, modelo simples com métricas, heap, trie, bases
numéricas, eletricidade básica e gerenciamento inteligente da comunicação).

O sistema roda inteiramente em terminal, por meio de um menu numérico, e não depende de
hardware real, sensores físicos ou APIs externas — todos os dados são simulados.

## 2. Descrição dos dados

O arquivo `dados_aurora_siger.csv` contém **60 registros simulados** de alertas/operação
dos módulos da colônia, com as colunas:

| Coluna | Descrição |
|---|---|
| `id_alerta` | identificador único do alerta (ex.: AL-001) |
| `modulo` | módulo de origem (Comunicação, Suporte Vital, Hidroponia etc.) |
| `codigo_sensor_hex` / `codigo_sensor_dec` | código do sensor em hexadecimal e decimal |
| `status` | Normal, Atenção ou Crítico (calculado a partir da criticidade e do atraso) |
| `criticidade` | nível de 1 (baixo) a 5 (altíssimo) |
| `latencia_prevista_ms` / `latencia_real_ms` | latência esperada vs. observada |
| `tensao_v` / `corrente_a` | grandezas elétricas simuladas do módulo |
| `tempo_desde_registro_min` | tempo decorrido desde o registro do alerta |
| `risco_operacional` | Baixo, Médio ou Alto |

Os dados foram gerados com NumPy (seed fixo = 42, portanto reprodutíveis) e organizados
com Pandas em `gerar_dados.py`.

## 3. Indicadores, erro absoluto e erro relativo

Para cada registro foi calculado:

- **Erro absoluto** = `|latência_real − latência_prevista|`
- **Erro relativo (%)** = `erro_absoluto / latência_real × 100`
- **Potência (W)** = `tensão × corrente` (grandeza elétrica do módulo)

Resultado na base completa:

- Erro absoluto médio de latência: **6,71 ms**
- Erro relativo médio de latência: **15,22 %**
- Potência média dos módulos: **11,21 W**

**Interpretação:** o erro absoluto mostra a diferença bruta entre previsão e
observação, mas módulos com latências típicas diferentes (ex.: um módulo de 10 ms
contra um de 100 ms) não podem ser comparados apenas pelo erro absoluto — por isso o
erro relativo é usado para normalizar essa comparação. Pequenas divergências numéricas
também podem surgir por arredondamento e representação em ponto flutuante (em Python,
por exemplo, `0.1 + 0.2` não resulta exatamente em `0.3`). A equipe adotou como critério
que um erro relativo **acima de 15%** é preocupante e deve acionar prioridade de
investigação; abaixo disso, o desvio é tratado como aceitável dentro da margem
operacional da colônia.

## 4. Modelo simples de previsão e avaliação de performance

Foi construído um modelo de **Regressão Linear** (scikit-learn) para prever a latência
real a partir de quatro atributos operacionais: `criticidade`, `tensao_v`, `corrente_a`
e `tempo_desde_registro_min`, com divisão treino/teste de 75%/25% (`random_state=42`).

| Métrica | Modelo (regressão) | Baseline (usar a própria latência prevista) |
|---|---|---|
| MAE | 27,12 ms | **7,27 ms** |
| RMSE | 31,82 ms | **9,86 ms** |
| MSE | 1.012,78 | — |
| R² | −0,30 | — |

**Interpretação:** o R² negativo indica que o modelo de regressão linear, usando apenas
os atributos operacionais escolhidos, performa **pior** do que simplesmente confiar na
latência já prevista pelo sistema de origem (baseline). Isso é um resultado honesto e
pedagogicamente relevante: mostra que criticidade, tensão, corrente e tempo de registro,
isoladamente, não explicam bem a variação de latência nesta base simulada — a própria
previsão original carrega mais informação sobre o comportamento real. O exercício reforça
a lição de que **um único número (R²) não basta** para julgar um modelo: é preciso olhar
MAE e RMSE junto, comparar com um baseline simples, e entender *por que* o modelo não
superou a referência, em vez de aceitar cegamente a métrica. Como apenas um modelo foi
avaliado (não houve comparação entre modelos alternativos), não foi necessário aplicar
AIC/BIC ou busca de hiperparâmetros (Grid/Random Search) — esses critérios seriam
relevantes se mais de uma arquitetura de modelo estivesse sendo comparada.

## 5. Heap — priorização de alertas

**Representação:** cada alerta é uma tupla `(prioridade, dados_do_alerta)`.

**Critério de prioridade** (função `calcular_prioridades`):
`prioridade = criticidade × 10 + atraso_de_latência × 0,5 + peso_do_risco + tempo_desde_registro × 0,05`

Isso combina criticidade cadastrada (peso principal), o quanto a latência real está
atrasada em relação à prevista, o risco operacional (Baixo/Médio/Alto) e um pequeno bônus
por tempo de espera, para evitar que alertas antigos sejam esquecidos.

**Organização:** foi implementado manualmente um **max-heap em vetor** (classe
`FilaPrioridade`), com os métodos `_subir` (heapify-up, usado na inserção) e
`_descer` (heapify-down, usado na extração do maior elemento), reproduzindo a lógica
estudada na disciplina em vez de depender apenas da biblioteca `heapq`.

**Seleção do mais urgente:** o alerta de maior prioridade está sempre na raiz do heap
(índice 0); `extrair_maior()` remove a raiz, substitui pelo último elemento e aplica
heapify-down para restaurar a propriedade de heap em O(log n).

**Vantagem sobre lista simples:** em uma lista não ordenada, encontrar o alerta mais
urgente custa O(n) (percorrer tudo), e mantê-la ordenada custaria O(n) por inserção. No
heap, tanto inserir quanto extrair o mais urgente custam **O(log n)**, o que é muito mais
eficiente à medida que novos alertas chegam continuamente — cenário realista para a
operação da Aurora Siger.

## 6. Trie — busca por prefixo

Foi implementada uma `Trie` clássica (nós com dicionário de filhos + marcador de fim de
palavra), usada para:

- Buscar módulos/palavras por prefixo (ex.: `"com"` → `comunicacao`, `comunicacao
  principal`, `comunicacao secundaria`);
- Buscar códigos de sensores em hexadecimal por prefixo (ex.: `"1"` → `0x10`, `0x16`,
  `0x17`, `0x1A`).

**Por que a trie é adequada:** em uma lista simples, comparar um prefixo com cada uma das
n palavras custa O(n × k), em que k é o tamanho do prefixo. Na trie, cada caractere do
prefixo corresponde a um único caminho na árvore, então a busca custa **O(k)**,
independentemente da quantidade de registros na base — o que acelera a localização de
módulos, sensores ou comandos à medida que a colônia (e seus dados) cresce.

## 7. Dispositivos, bases numéricas e eletricidade básica

- **Entrada de dados:** sensores simulados de tensão/corrente por módulo, contadores de
  latência e registradores de criticidade/risco (representados nas colunas do CSV).
- **Saída de dados:** o próprio terminal do SCIC funciona como "dashboard" textual,
  exibindo tabelas, rankings de prioridade e relatórios de análise.
- **Interfaces de comunicação (conceituais):** rede interna entre módulos, possivelmente
  via barramento Wi-Fi/Bluetooth de curto alcance ou cabeamento USB entre
  microcontroladores dos sensores — citadas apenas de forma conceitual, sem implementação
  real.
- **Bases numéricas:** os códigos de sensores são representados em decimal, binário e
  hexadecimal (ex.: um código decimal `214` corresponde a `11010110` em binário e a
  `0xD6` em hexadecimal), com conversão feita pela funcionalidade 8 do menu.
- **Eletricidade básica:** a potência de cada módulo é calculada por `P = V × I`; o
  sistema também permite calcular a resistência equivalente pela Lei de Ohm
  (`R = V / I`). Exemplo: um módulo de comunicação com tensão de 5 V e corrente de 0,5 A
  consome **2,5 W**, com resistência equivalente de 10 Ω.

## 8. Gerenciamento inteligente da comunicação

Os próprios resultados do SCIC ilustram, em escala reduzida, como uma rede de
comunicação inteligente funcionaria na Aurora Siger:

- **Sensores e medidores inteligentes** forneceriam continuamente os dados que hoje são
  simulados no CSV (latência, tensão, corrente), alimentando o sistema em tempo real.
- **Monitoramento contínuo:** com 43,3% dos alertas classificados como Críticos e 30,0%
  em Atenção nesta base, fica claro que um monitoramento constante (e não pontual) é
  necessário para não deixar falhas se acumularem.
- **Automação de decisões rápidas:** o heap de prioridades automatiza a pergunta "qual
  alerta tratar primeiro?", algo essencial em situações críticas, quando não há tempo de
  analisar manualmente cada registro.
- **Redundância e armazenamento de dados:** como o erro relativo médio de latência foi de
  15,22% (acima do limite que a equipe definiu como aceitável), enlaces redundantes e
  armazenamento local de dados ajudariam a manter a estabilidade da base mesmo quando um
  canal de comunicação degrada.
- **Manutenção preditiva:** o modelo de previsão (mesmo tendo performado abaixo do
  baseline) mostra o tipo de abordagem que, com mais dados e variáveis, poderia antecipar
  degradações de latência antes que se tornem falhas, reduzindo paradas não planejadas.
- **Redes inteligentes de comunicação e microrredes:** a busca por prefixo (trie) e a
  priorização (heap) são blocos básicos de uma rede que precisa escalar — à medida que a
  colônia cresce, localizar módulos/sensores rapidamente e priorizar automaticamente os
  alertas mais urgentes são exatamente os mecanismos que sustentam microrredes de energia
  e comunicação mais autônomas.

## 9. Reflexão social, cultural e sustentável

**a) Uso eficiente da comunicação e sustentabilidade:** ao priorizar automaticamente os
alertas mais críticos (heap) em vez de tratar tudo com a mesma urgência, o SCIC evita
desperdício de tempo e de energia da equipe humana e dos próprios módulos de comunicação,
concentrando esforço onde ele é realmente necessário — um princípio de eficiência
diretamente ligado à sustentabilidade operacional de uma colônia com recursos limitados.

**b) Conhecimentos tradicionais e respeito à natureza:** povos indígenas historicamente
desenvolveram sistemas de observação contínua do ambiente (clima, solo, ciclos naturais)
para tomar decisões coletivas de forma responsável, sem desperdício de recursos. Esse
princípio de observar antes de agir, e de não extrair mais do que o necessário, inspira
diretamente a lógica de monitoramento contínuo e manutenção preditiva adotada no SCIC: em
vez de reagir somente depois que um módulo falha, o sistema busca antecipar problemas e
usar os recursos da colônia de forma equilibrada.

**c) Responsabilidade humana sobre decisões automatizadas:** o SCIC prioriza e sugere,
mas não decide sozinho quais ações tomar diante de um alerta crítico — a equipe humana
continua responsável por validar e agir. Isso é intencional: um sistema de prioridades
baseado em números (criticidade, atraso, risco) pode errar ou refletir más definições de
peso, então a supervisão humana evita que decisões automatizadas tenham consequências não
previstas sobre a segurança da colônia.

## 10. Limitações e possíveis melhorias

- Os dados são simulados; em um cenário real, seria necessário validar os pesos usados na
  fórmula de prioridade do heap com especialistas da missão.
- O modelo de regressão linear performou abaixo do baseline nesta base simulada — uma
  melhoria natural seria testar mais atributos (ex.: módulo de origem como variável
  categórica) ou modelos não lineares.
- A trie atual não trata acentuação; nomes de módulos foram cadastrados sem acentos para
  simplificar a busca, mas uma versão futura poderia normalizar acentos automaticamente.
- O sistema não possui persistência de alterações (cadastros feitos na sessão não são
  salvos de volta no CSV); isso poderia ser adicionado com `df.to_csv()` ao final da
  execução.
