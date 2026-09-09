# Aurora Siger — NCAS (Núcleo Cognitivo da Aurora Siger)

Protótipo de um sistema de apoio à decisão para a colônia marciana **Aurora Siger**, utilizando arquivos texto e JSON, álgebra booleana com simplificação de expressões e engenharia de prompts em Python puro para organizar registros operacionais, classificar alertas e simular interações com um assistente inteligente.

## Link do Vídeo

[[link do vídeo no YouTube](https://youtu.be/FxAyOORM8Q0)]

---

## Organização

    fase5/
    ├── codigo_fonte.py                      # ponto de entrada do sistema
    ├── dados_colonia.json                   # módulos e alertas operacionais da colônia
    ├── registros_colonia.txt                # log sequencial de interações
    ├── regras_logicas.pdf                   # expressões booleanas e simplificações
    ├── prompts_utilizados.pdf               # prompts criados e explicação de cada um
    ├── link_video.txt                       # link do vídeo de apresentação
    └── relatorio.pdf                        # documentação complementar

---

## O que o sistema faz

- Organiza os dados da colônia em **duas camadas de persistência**, com critério explícito:
  - `dados_colonia.json` — registros com campos fixos que o sistema precisa consultar e filtrar
  - `registros_colonia.txt` — eventos cronológicos, gravados em modo *append*
- Reaproveita os **13 módulos da Fase 4**, com os mesmos nomes, tipos, consumo e prioridade operacional
- Mantém, para cada alerta operacional: módulo de origem, tipo de ocorrência, prioridade, data, mensagem e as condições booleanas da análise
- Aplica **duas regras booleanas simplificadas** na análise de um alerta:
  - Controle de acesso ao módulo, distinguindo as duas causas possíveis de bloqueio
  - Classificação automática de criticidade, cruzando o alerta com a prioridade real do módulo
- Prova a equivalência entre a forma original e a simplificada de cada regra por **tabela-verdade executável**
- Gera **quatro prompts estruturados** a partir dos dados reais de cada alerta
- **Simula respostas do assistente** derivadas das regras lógicas, sem integração com API externa
- Compara **prompt vago × prompt refinado** como análise de otimização de resposta
- Registra toda interação em log, preservando o histórico entre execuções
- Permite cadastrar novos alertas pelo terminal, com validação de módulo e de entrada

---

## Regras Lógicas Utilizadas

| Regra | Expressão Original | Expressão Simplificada | Teorema | Ganho |
|---|---|---|---|---|
| **Bloqueio de acesso** | `NOT (AUTORIZADO AND MODULO_ATIVO)` | `(NOT AUTORIZADO) OR (NOT MODULO_ATIVO)` | De Morgan | Causa do bloqueio identificável |
| **Criticidade do alerta** | `(FALHA AND MOD_CRITICO) OR (FALHA AND CONSUMO_ALTO)` | `FALHA AND (MOD_CRITICO OR CONSUMO_ALTO)` | Distributiva | 3 operações → 2 |

As duas formas de cada regra permanecem implementadas no código. A função `tabela_verdade()`, acionada pela opção 4 do menu, avalia ambas para todas as combinações possíveis de entrada e compara os resultados — 12 linhas de prova de equivalência. Detalhamento em `regras_logicas.pdf`.

---

## Estruturas de Dados Utilizadas

- `dict` → registro individual de módulo e de alerta; acesso O(1) por chave, espelhando a estrutura do JSON
- `list[dict]` → coleções de módulos e alertas, percorridas por busca linear em `buscar_modulo()` e `buscar_alerta()`
- `tuple` → conjuntos imutáveis de valores nas tabelas-verdade e retorno múltiplo em `condicoes_do_alerta()`
- `bool` → variáveis das expressões booleanas, avaliadas com `and`, `or` e `not`
- `str` (f-strings) → montagem dos prompts com injeção de dados e formatação alinhada da saída
- Módulo `json` → serialização (`dump` / `dumps`) e desserialização (`load`) entre memória e disco
- Módulo `datetime` → carimbo de tempo dos registros de log

---

## Engenharia de Prompts

| Técnica | Tarefa no sistema | Formato da saída |
|---|---|---|
| **Zero-shot** | Resumir o alerta em uma frase para o Centro de Comando | Texto livre curto |
| **Few-shot** | Classificar a urgência a partir de exemplos resolvidos | URGENTE / MODERADA / BAIXA |
| **Chain-of-Thought** | Decidir a criticidade expondo o raciocínio passo a passo | Passo a passo + conclusão |
| **Structured Output** | Resposta padronizada e consumível por outro programa | JSON com 4 chaves fixas |

Os prompts são **funções, não textos fixos**: cada um recebe o alerta e o módulo correspondente e injeta os dados reais no molde, de modo que trocar o alerta muda o prompt gerado. As respostas simuladas derivam das regras booleanas do sistema — apenas a redação final é predefinida. O prompt *chain-of-thought* reproduz, em linguagem natural, a mesma expressão booleana que o programa avalia em Python. Detalhamento em `prompts_utilizados.pdf`.

---

## Memória, Armazenamento e Fluxo de Dados

Ao cadastrar um alerta, o dicionário existe na **memória RAM** apenas durante a execução. A operação de escrita `json.dump()` transfere esse dicionário para o **armazenamento em disco**; em uma execução seguinte, `json.load()` percorre o caminho inverso, trazendo o conteúdo do disco de volta para a memória. O mesmo ciclo vale para o log em texto, com `write` em modo *append* na gravação e `read` / `readlines` na leitura.

O fluxo completo é:

    entrada pelo teclado -> processamento em memória -> escrita em armazenamento
    persistente -> leitura em execução futura

A opção 8 do menu (*Recarregar dados do JSON*) torna esse ciclo observável: ela descarta o dicionário em memória e relê o arquivo do disco, evidenciando a diferença entre memória volátil e armazenamento persistente.

---

## Ética, Diversidade e Responsabilidade

- **Vieses** — as respostas do assistente são geradas por templates que codificam critérios definidos por quem escreveu o sistema. Em um sistema real, esses critérios viriam dos dados de treinamento e carregariam os vieses presentes neles; um núcleo cognitivo que prioriza atendimento pode, sem decisão explícita de ninguém, despriorizar sistematicamente setores, turnos ou grupos da tripulação
- **Diversidade** — equipes diversas identificam vieses que equipes homogêneas não enxergam, porque reconhecem os padrões que as afetam; a composição de quem constrói o sistema é uma variável técnica, não apenas social
- **Decisão sobre fatos** — a criticidade é determinada pela prioridade operacional cadastrada do módulo, e não pelo rótulo de urgência que o operador digitou, reduzindo a influência de julgamento subjetivo
- **Auditabilidade** — cada análise imprime a expressão booleana e os valores de entrada que produziram o resultado; uma decisão que pode ser explicada é uma decisão que pode ser contestada
- **Linguagem** — as respostas automáticas usam terminologia técnica e neutra, referindo-se a módulos e ocorrências, nunca a juízos sobre pessoas
- **Responsabilidade humana** — ao final de cada análise o sistema declara que a decisão final cabe à equipe humana do Centro de Comando; o sistema **sugere**, a pessoa **decide**

---

## Menu do Sistema

```
 1. Cadastrar alerta operacional
 2. Consultar modulos e alertas salvos
 3. Analisar alerta operacional
 4. Executar validacao logica (tabelas-verdade)
 5. Exibir prompts estruturados
 6. Simular resposta do assistente
 7. Analise de otimizacao de prompt
 8. Recarregar dados do JSON
 9. Ver logs de acesso
 0. Sair
```

---

## Como Rodar

Requer apenas Python 3 (biblioteca padrão, sem dependências externas):

    python codigo_fonte.py

Execute a partir de dentro da pasta `fase5/` — os caminhos dos arquivos de dados são relativos. Navegue pelo menu digitando o número da opção desejada.
