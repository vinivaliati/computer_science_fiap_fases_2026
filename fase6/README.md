# SCIC — Sistema de Comunicação Inteligente da Colônia (Missão Aurora Siger)

# Objetivo do projeto

O SCIC é um sistema em terminal que organiza, analisa e prioriza dados simulados de
comunicação e operação da colônia marciana Aurora Siger. O projeto aplica, de forma
prática, os conteúdos estudados até esta fase: organização de dados com Pandas, cálculo
de erro absoluto e relativo, um modelo simples de previsão avaliado com métricas (MAE,
MSE, RMSE, R²), estrutura de **heap** para priorização de alertas, estrutura de **trie**
para busca por prefixo, bases numéricas (decimal/binário/hexadecimal) e eletricidade
básica aplicada à comunicação.

# Arquivos da entrega

| Arquivo | Descrição |
|
| `codigo_fonte.py` | **Arquivo principal do sistema.** Menu de terminal com todas as funcionalidades. |
| `gerar_dados.py` | Script auxiliar usado para gerar `dados_aurora_siger.csv` (dados simulados, seed fixo = 42). |
| `gerar_graficos.py` | Script auxiliar que lê `dados_aurora_siger.csv` e gera o gráfico de apoio. |
| `dados_aurora_siger.csv` | Base de dados simulada (60 registros de alertas/operação dos módulos). |
| `relatorio_tecnico.md` | Relatório técnico completo: contexto, dados, métricas, heap, trie, bases numéricas, gerenciamento inteligente e reflexão social/cultural/sustentável. |
| `graficos_ou_imagens/analise_latencia_status.png` | Gráfico de apoio (gerado por `gerar_graficos.py`): latência prevista vs. real e distribuição de alertas por status. |
| `link_video.txt` | Link do vídeo de apresentação (YouTube, "Não listado"). |
| `README.md` | Este arquivo. |

## Dependências

- Python 3.9+
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib` (usada somente em `gerar_graficos.py`, para desenhar o gráfico de apoio;
  **não é necessária** para rodar `codigo_fonte.py`)

Instalação (caso necessário):

 bash
pip install pandas numpy scikit-learn matplotlib


Nenhuma biblioteca além dessas, e nenhuma integração externa (API, hardware real, rede),
é necessária para executar o sistema.

# Como executar

1. Deixe `codigo_fonte.py` e `dados_aurora_siger.csv` na mesma pasta.
2. No terminal, rode:

  bash
python3 codigo_fonte.py


3. Use o menu numérico para navegar entre as funcionalidades:


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


**Sugestão de uso:** comece pela opção **1** (carregar dados) antes de usar as demais
funcionalidades.

# Exemplo de execução


Escolha uma opcao: 1
60 registros carregados de 'dados_aurora_siger.csv'.

Escolha uma opcao: 6
Quantos alertas mais urgentes deseja ver? (padrao 5): 3

ID        Modulo                    Status    Criticidade Prioridade
AL-027    Comunicacao Principal     Critico   5           62.4
AL-014    Suporte Vital             Critico   5           58.1
AL-033    Controle Ambiental        Atencao   4           49.7


# Observações

- Os dados são 100% simulados (seed fixo em `gerar_dados.py`), sem uso de sensores
  físicos, APIs externas ou hardware real.
- O heap de priorização foi implementado manualmente (sem depender apenas da biblioteca
  `heapq`), para evidenciar o uso de heapify-up e heapify-down estudados na disciplina.
- Alterações feitas via "Cadastrar novo registro" valem apenas para a sessão atual (não
  são salvas de volta no CSV).
