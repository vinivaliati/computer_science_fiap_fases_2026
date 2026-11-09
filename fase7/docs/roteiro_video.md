# Roteiro do vídeo (máx. 5 min) e pitch

Dica: ensaie uma vez; terminal em fonte grande; abra o Tinkercad e o `circuito_logico.png` antes de gravar.

| Tempo | O que mostrar | O que falar |
|---|---|---|
| 0:00–0:25 | Tela do menu | Apresentar equipe e o SIFSM: protótipo de energia e consumo da Aurora Siger; os dados são simulados (8 módulos × 6 ciclos = 48 leituras) |
| 0:25–1:05 | Menu 1: listar, cadastrar com bateria 150% (erro do banco), alterar com `abc`, excluir | Banco SQLite com `CHECK`/`UNIQUE`; CRUD; `try/except/else/finally`; o `finally` fecha a conexão |
| 1:05–1:30 | Menu 2: analisar e tabela verdade | Regra `RISCO = (B E) OU (C T)`; 2 riscos, 3 alertas |
| 1:30–2:20 | `circuito_logico.png` (5 s), depois o Tinkercad com o Monitor Serial aberto (demo abaixo) | Mesma lógica em hardware: as 4 entradas viram B, E, C, T e as saídas são os LEDs e o buzzer |
| 2:20–2:40 | Menu 3: fila, histórico, busca, impacto de falha | Heap, pilha, hash e grafo: por que cada um |
| 2:40–3:15 | Menu 4: gráfico de SoC | Integral do saldo de energia, método do trapézio, tempestade de poeira |
| 3:15–3:40 | Menu 5 | Regressão simples (coeficiente e previsão) e múltipla (MAE/R²); cuidado com o R² alto |
| 3:40–4:05 | Menu 7 → opção 1 (Gemini real): fluxo, pedido bloqueado ("excluir registros") e tracing | Três agentes com ferramentas, handoffs, guardrails e decisão humana. Teste a chave antes de gravar |
| 4:05–4:25 | Menu 8 | NumPy ≈ 30× mais rápido; CPU/GPU/NPU e movimentação de dados |
| 4:25–4:50 | Seção 10 do `relatorio_tecnico.md` na tela | Sustentabilidade, cidadania digital e impacto socioambiental (fala abaixo) |
| 4:50–5:00 | Tela do menu | Encerramento com o pitch: a IA só sugere e quem decide é o humano |

## Demo do Tinkercad (50 s)
Antes de gravar: deixe a simulação pronta, com o Monitor Serial aberto, bateria alta, consumo baixo e a chave em "essencial".

1. **Normal (10 s):** bateria alta, consumo baixo, temperatura 25 °C ou menos → **LED verde**, Monitor mostra `-> NORMAL`. Falar: "NOT alerta".
2. **Alerta (10 s):** abaixar o potenciômetro da bateria para menos de 25% com a chave desligada → **LED amarelo**, `-> ALERTA`. Falar: "B OU C OU T".
3. **Risco por bateria (10 s):** ligar a chave (módulo essencial) com a bateria baixa → **LED vermelho + buzzer**, `-> RISCO`. Falar: "B E E".
4. **Risco por consumo e calor (15 s):** voltar a bateria para alta e desligar a chave; subir o consumo acima de 120% (potenciômetro acima de 60%) e a temperatura do TMP36 acima de 26 °C → **LED vermelho + buzzer**. Falar: "C E T".
5. Fechar mostrando o Monitor Serial: as colunas B, E, C, T batem com a regra do menu 2.

## Fala de sustentabilidade (25 s, com a seção 10 do relatório na tela)
"A IA pode fazer verificações perigosas para o corpo humano longe da Terra, mas cria risco de dependência e de vigilância; por isso ela só sugere, quem decide é o humano, e há plano B manual. Usamos só dados de módulos, sem dados pessoais, e o guardrail bloqueia esse tipo de pedido. A diversidade da tripulação deve orientar limites e prioridades. Tudo isso está na seção 10 do relatório."

O roteiro soma exatamente 5:00 (sobra o fim para a demo do Tinkercad, se precisar). Ensaie e corte onde sobrar, porque o vídeo não pode passar de 5 min.

**Pitch (30 s):** "A Aurora Siger precisa saber quando a energia vai faltar antes que falte. O SIFSM junta banco de dados, lógica, simulação e um modelo linear para prever o consumo e avisar o risco, e uma IA com guardrails que só sugere: quem decide é o humano."

Depois de gravar: publicar no YouTube como **Não listado** e colar o link em `link_video.txt`.
