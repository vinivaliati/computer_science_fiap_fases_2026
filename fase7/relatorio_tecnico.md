# Relatório Técnico — SIFSM
**Sistema Integrado de Futuro Sustentável em Marte · Colônia Aurora Siger · Fase 7**

## Sumário
1. Contexto da solução · 2. Dados · 3. Banco de dados e CRUD · 4. Regra lógica e circuito · 5. Estruturas de dados · 6. Simulação e matemática · 7. Modelagem linear · 8. IA integrada · 9. Arquitetura computacional · 10. Sustentabilidade e cidadania digital · 11. Limitações e melhorias · 12. Uso de ferramentas de IA

## 1. Contexto da solução
A sustentabilidade da colônia depende de energia, dados e decisões integradas. O SIFSM foca em **energia e consumo dos módulos**: guarda as leituras, detecta risco, simula a bateria, prevê o consumo e sugere ações. É um protótipo com dados simulados, sem sensores reais nem APIs externas.

## 2. Dados utilizados
`dados_aurora_siger.csv`: 8 módulos (MOD-EN-001 a MOD-CM-008) × 6 ciclos = 48 registros, com consumo, geração, bateria, temperatura, ocupação, status e prioridade. Foram gerados por script com semente fixa e alguns eventos inseridos de propósito (picos de consumo da mineração e da agricultura, queda de geração no ciclo 4, baterias baixas nos ciclos 5 e 6). **Não são medições reais.**

## 3. Banco de dados e CRUD
SQLite (`aurora_siger.db`), tabela `registros` criada por `script_banco.sql`. As regras ficam no próprio banco: `CHECK` (bateria 0–100, status válido, consumo ≥ 0) e `UNIQUE (codigo_modulo, ciclo)`. Assim qualquer programa que grave nele respeita as regras.

O CRUD está em `modulos/dados.py`: cadastrar, listar (todos, por módulo, status ou ciclo), alterar e excluir (com confirmação). Tratamento de erros:
- `try/except/else/finally` em toda escrita: `IntegrityError` (violação de CHECK/UNIQUE), `sqlite3.Error` genérico e `finally` que sempre fecha a conexão;
- `ValueError` na conversão de entradas (texto no lugar de número, status inválido), com nova tentativa;
- `FileNotFoundError` se SQL ou CSV não existirem;
- consultas usam parâmetros `?`, e o nome do campo é conferido contra uma lista fixa (evita SQL injection).

Testado: bateria 150% (recusada pelo banco), `abc` no campo numérico, status inexistente, id 999 e exclusão repetida, sem que o programa caísse.

## 4. Regra lógica e circuito
Variáveis: **B** bateria < 25%; **E** módulo essencial (energia, suporte à vida, habitação); **C** consumo > 120% da média do próprio módulo; **T** temperatura > 26 °C.

```
RISCO  = (B AND E) OR (C AND T)
ALERTA = B OR C OR T
NORMAL = NOT ALERTA
```
Resultado nos 48 registros: **2 em risco** (suporte à vida no ciclo 6 e mineração no ciclo 5), **3 em alerta**, 43 normais. A tabela verdade completa (16 linhas) está no menu 2.

Circuito: `circuito_logico.png` (bloco 1: duas portas AND e uma OR para o risco; bloco 2: uma OR de 3 entradas para o alerta e uma NOT para o normal). No Tinkercad (projeto em `link_tinkercad.txt`, esquemático em `graficos_ou_imagens/esquematico_tinkercad.pdf`): potenciômetro (bateria, A0), TMP36 (temperatura, A1), potenciômetro (consumo, A2), chave (essencial, D2); saídas LED vermelho + buzzer (risco), LED amarelo (alerta) e LED verde (normal). `modulos/hardware.py` reproduz a mesma lógica em Python e imprime 5 cenários.

## 5. Estruturas de dados
| Estrutura | Onde | Por quê |
|---|---|---|
| Heap (`heapq`) | Fila de alertas | O mais urgente sai primeiro, sem reordenar tudo |
| Pilha (`list`) | Histórico de ações do CRUD | A última ação aparece primeiro (LIFO) |
| Tabela hash (`dict`) | Índice de módulos por código | Busca direta pela chave |
| Grafo + BFS | Dependência entre módulos | Mostra quem para quando um módulo falha (ex.: falha da mineração afeta logística, agricultura e suporte à vida) |

O grafo de dependências é uma hipótese de projeto, não um dado real.

## 6. Simulação computacional e matemática
Estado de carga como **integral do saldo de potência**: `SoC(t) = SoC0 + (1/C) · ∫ [g(s) − c(s)] ds`, com capacidade C = 300 kWh (hipótese) e SoC0 = 60%.
- Geração `g(t)`: meia senoide entre 6 h e 18 h, com `P_max = E_dia · π/24` (pois ∫ P·sen(π(t−6)/12) dt em [6,18] = 24P/π).
- Consumo `c(t)`: média do ciclo com variação de ±15% (mais uso à noite).
- Integração numérica pela regra do trapézio (passo 0,05 h). Conferência com o valor exato: erro < 0,01 kWh.
- Cenários: normal e **tempestade de poeira** (geração a 40%).

Resultados: no ciclo 1 normal o SoC termina em 65,9%; em tempestade cai a 8,7% (2,7 h abaixo de 20%). No ciclo 4 (geração menor) termina em 32,3% e, em tempestade, chega a 0% por 7 h. Gráficos em `graficos_ou_imagens/`. A geração média diária também é calculada (média de função = integral / 24 h).

## 7. Modelagem linear
**Análise exploratória:** consumo médio de 36,4 kWh por registro; correlações com o consumo: ciclo 0,08, temperatura 0,21, ocupação 0,14, bateria −0,41.

**Simples (consumo total × ciclo):** `consumo = 270,2 + 5,93 · ciclo` (R² = 0,61). Interpretação: o consumo total cresce cerca de 5,9 kWh por ciclo. Previsão: 311,7 kWh no ciclo 7, acima da geração média (284,2 kWh): sinal de que será preciso ampliar geração ou cortar cargas.

**Múltipla (consumo do módulo × tipo, ciclo, temperatura, ocupação):** treino 36 / teste 12 registros. MAE 1,57, RMSE 1,80, R² 0,98, contra baseline pela média com MAE 12,5 e R² −0,07. Os coeficientes maiores vêm do **tipo do módulo** (referência: agricultura): comunicação −35,2, laboratório −32,1, mineração +13,5. Temperatura +0,65 kWh por °C, ciclo +0,22. **Atenção:** o R² alto vem principalmente do tipo (módulos têm consumos-base muito diferentes), e com 48 registros há risco de superajuste; por isso comparamos com o baseline e tratamos o resultado como demonstração do método.

## 8. IA integrada (agentes e guardrails)
Implementada em `modulos/agentes.py` e `modulos/llm.py` com **LLM real (API do Gemini)**, via `urllib` da biblioteca padrão e chave em `.env` fora do git. Fluxo: pedido → guardrail de entrada → **Monitor** (ferramenta `listar_alertas`) → handoff → **Analista** (ferramenta `simular_cenario`, que sem ciclo informado usa o mais crítico) → handoff → **Planejador** (ferramentas `impacto_falha` e `buscar_procedimento`, uma base de procedimentos por tema, um RAG simples com citação de fonte) → guardrail de saída → decisão humana. Cada agente é uma chamada ao modelo com um papel (instrução) e uma lista **permitida** de ferramentas; o modelo decide quando chamá-las (function calling) e o nosso código executa e devolve o resultado, com no máximo 5 voltas por agente.
- Guardrails: (1) entrada: bloqueia pedidos de excluir/alterar/desligar e de dados pessoais; (2) ferramentas: cada agente só vê as suas, qualquer outra chamada é recusada e registrada, e os argumentos vindos do modelo são validados (ex.: `fator_geracao` entre 0 e 1,5); (3) nenhuma ferramenta altera o banco; (4) saída: toda recomendação é marcada como sugestão que exige aprovação humana.
- Privacidade: só vão para a API dados simulados e agregados de módulos, sem dados pessoais. A chave fica no `.env` (ignorado pelo git).
- Tracing: cada passo é registrado e pode ser exibido (menu 7, opção 3); a sessão guarda o pedido.
- **Fallback:** sem chave ou sem rede, o sistema usa um fluxo determinístico (mesmas ferramentas, sem modelo) e avisa "[simulado]" na tela, então a demonstração nunca depende da internet. Respostas de LLM variam entre execuções; por isso os números vêm sempre das ferramentas, e o prompt proíbe inventar valores.

## 9. Arquitetura computacional
`modulos/arquitetura.py` mede 2 milhões de pontos da curva solar: laço Python 0,38 s × NumPy vetorizado 0,012 s (**≈ 31× mais rápido**, mesmo resultado). O ganho vem de aplicar a mesma operação a vários dados de uma vez (SIMD) em código compilado.
- **CPU** roda menu, banco e regras (decisões sequenciais).
- **GPU** compensaria se simulássemos centenas de cenários independentes (paralelismo de dados).
- **NPU/TPU** seriam úteis para rodar modelos de IA na colônia com pouca energia, sem depender da Terra (atraso de 3 a 22 minutos).
- **Memória e largura de banda:** o gargalo do protótipo é mover dados (banco → DataFrame → arrays), não calcular. Manter dados perto de quem calcula economiza energia; chiplets e computação heterogênea reduzem essa movimentação.
- Para este problema, um modelo linear pequeno em CPU basta e consome muito menos que uma rede grande.

## 10. Sustentabilidade, cidadania digital e impacto socioambiental
Escolhemos sete dos pontos pedidos no enunciado e ligamos cada um a algo que o SIFSM faz.

| Ponto | Como aparece no SIFSM |
|---|---|
| Uso responsável dos recursos | A regressão prevê um consumo de 311,7 kWh no ciclo 7, acima da geração média de 284,2 kWh. O menu 9 então recomenda ampliar a geração ou cortar cargas não essenciais antes desse ciclo. |
| Simulação e redução de desperdício | A simulação da bateria mostra antes de acontecer o efeito de uma tempestade de poeira: no ciclo 4 a carga chega a 0% e fica assim por 7 h. Com isso dá para preparar o modo econômico e proteger o suporte à vida, em vez de descobrir a falta de energia na hora. |
| Armazenamento, resiliência e autonomia | A bateria é o que segura a colônia na tempestade, e a regra de risco dá prioridade aos módulos essenciais (energia, suporte à vida e habitação). Os agentes têm um fluxo simulado que roda sem internet, para o caso de a comunicação falhar (o atraso com a Terra é de 3 a 22 minutos). |
| Cidadania digital e transparência | Cada passo dos agentes fica registrado no tracing (menu 7, opção 3) e o histórico do CRUD guarda as últimas ações. A recomendação é sempre uma sugestão, e a decisão final é de uma pessoa. |
| Economia dos dados | O banco guarda só dados de módulos, e a ocupação é um percentual agregado. O guardrail de entrada recusa pedidos de dados pessoais. Se um dia o sistema guardasse dados da tripulação, como saúde ou localização, seria preciso coletar o mínimo e restringir quem acessa, porque quem controla esses dados passa a ter poder sobre pessoas que não podem sair da colônia. |
| IA e impacto ambiental | Usamos regressão linear em CPU, que é leve. O benchmark do menu 8 mostra que calcular com NumPy é cerca de 31 vezes mais rápido que um laço em Python. A única parte que usa um modelo de linguagem grande são os agentes (API do Gemini), que rodam em data center; em Marte cada kWh gasto em computação faz falta ao suporte à vida. |
| Inovação e diversidade | O benefício é o sistema fazer verificações que seriam perigosas para as pessoas. O risco é a tripulação depender dele e perder a prática, por isso a equipe deve manter procedimentos manuais. Para a diversidade, o alerta é luminoso e sonoro (LED e buzzer) e os limites de 25%, 26 °C e 120% ficam em constantes no `modulos/regras.py`, para a comunidade poder revê-los. |

## 11. Limitações e possíveis melhorias
- Dados simulados (48 registros, 6 ciclos); limites, capacidade da bateria e grafo de dependências são hipóteses.
- Regressão múltipla com poucos dados e forte efeito do tipo de módulo; tendência por ciclo com apenas 6 pontos.
- A regra usa a média do módulo, que já inclui os próprios picos (ex.: pico da mineração no ciclo 3 aparece só como alerta de temperatura).
- Os agentes dependem de internet e de chave de API para funcionar com LLM (há fallback simulado); a resposta do modelo pode variar e deve ser conferida por um humano.
- Melhorias: dados reais/telemetria, validação cruzada, modelo por módulo, banco Oracle, painel web, memória de sessão persistente entre pedidos, avaliação automática da qualidade das respostas.

## 12. Uso de ferramentas de IA
A equipe contou com o apoio do Claude Code (Anthropic) na execução de algumas etapas do código. Todas as decisões do projeto (escolha do problema, regras, estruturas, modelos e arquitetura) e a revisão do que foi gerado foram feitas pelo grupo, que testou o sistema e conhece o funcionamento de cada parte.
