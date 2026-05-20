# Fase 3 — Atividade: Sistema Integrado da Colônia

---

## 1. Atividade Detalhada

A equipe deverá desenvolver um sistema integrado que represente o funcionamento inteligente da colônia, reunindo de forma organizada tudo o que foi trabalhado ao longo da fase.

### 1.1 Organizar os Dados da Colônia

- Armazenar energia, consumo e clima em estruturas como listas ou chave-valor
- Representar os sistemas da colônia de forma hierárquica (ex.: sistema energético → solar / eólico)
- Navegar entre subsistemas usando listas, tabelas chave-valor e organização hierárquica

### 1.2 Tomar Decisões Automaticamente

- Criar regras básicas — ex.: `se energia < 50 → reduzir consumo`
- Combinar condições — ex.: `se energia < 50 E consumo alto → ativar modo economia`
- Priorizar o que é mais importante — ex.: manter suporte à vida ligado e desligar sistemas não essenciais
- Gerar uma ação clara:

```
Entrada : energia = 40, consumo = 70
Saída   : "ALERTA: reduzir consumo"
```

### 1.3 Prever Comportamentos Simples (Regressão)

Organizar os dados em listas, ajustar uma reta e usá-la para estimar valores futuros:

```
vento  = [8, 10, 12]
energia = [20, 25, 30]

Entrada : vento = 11
Saída   : previsão de energia ≈ 27
```

### 1.4 Analisar o Uso de Energia

Comparar geração, consumo e reserva de energia:

```
Entrada : geração = 40, consumo = 70
Saída   : "ALERTA: consumo maior que geração"

Entrada : geração = 80, consumo = 30
Saída   : "SUGESTÃO: armazenar energia excedente"
```

---

## 2. Entregáveis Obrigatórios

### 2.1 Repositório GitHub (Público)

- Código em Python organizado em funções
- Estrutura clara com separação de lógica, dados e decisões
- `README.md` com explicação simples do funcionamento e exemplo de entrada e saída

### 2.2 Relatório em PDF

- Como os dados foram organizados
- Quais regras de decisão foram utilizadas
- Qual foi o modelo de previsão aplicado
- Como o sistema ajuda a melhorar o uso de energia na colônia
- Link do repositório GitHub público

---

## 3. Critérios de Avaliação

| Critério | Peso |
|---|:---:|
| Estruturação de dados | 2 |
| Lógica de decisão | 2 |
| Modelagem e previsão | 2 |
| Implementação em Python | 2 |
| Documentação e organização | 2 |

---

## 4. Observações

- Utilizar apenas conceitos trabalhados nos capítulos
- Não é necessário utilizar bibliotecas avançadas
- O foco está na lógica, organização e interpretação

---

## 5. Objetivo Final

Ao final da atividade, espera-se que a equipe seja capaz de:

- Organizar dados de forma eficiente
- Criar sistemas de decisão baseados em lógica
- Aplicar modelos matemáticos para previsão
- Desenvolver soluções computacionais integradas
- Evoluir de sistemas reativos para sistemas preditivos