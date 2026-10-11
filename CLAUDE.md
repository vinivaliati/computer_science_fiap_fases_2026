# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este repositório

Entregas em grupo do curso de Ciência da Computação da FIAP (2026). Cada pasta `faseN/` é uma **atividade integradora independente**, entregue e avaliada separadamente. Todas compartilham a mesma narrativa (a missão/colônia marciana **Aurora Siger**), mas não compartilham código: não há pacote comum, build, suíte de testes, linter ou CI.

Todo o conteúdo (código, identificadores, comentários, READMEs, commits) é em **português**. Mantenha assim.

## Como rodar cada fase

Os scripts usam caminhos relativos para dados e imports, então **execute sempre de dentro da pasta da fase**, não da raiz.

| Fase | Sistema | Comando (dentro de `faseN/`) | Dependências |
|---|---|---|---|
| 1 | Telemetria pré-decolagem | `jupyter notebook aurora_singer.ipynb` | `pip install -r requirements.txt` |
| 2 | MGPEB (pouso) | `python code.py` | stdlib |
| 3 | MGCE (gestão energética) | `python main.py` | stdlib |
| 4 | SIGIC (grafo da colônia) | `python codigo_fonte.py` | stdlib |
| 5 | NCAS (regras booleanas + prompts) | `python codigo_fonte.py` | stdlib |
| 6 | SCIC (comunicação) | `python codigo_fonte.py` | `pandas numpy scikit-learn` (+ `matplotlib` só para `arquivos_auxiliares/gerar_graficos.py`) |
| 7 | (a definir) | ainda não iniciada (README é placeholder) | nenhuma |

As fases 4, 5 e 6 são menus interativos de terminal (`input()` em loop); para exercitá-las sem interação, alimente as opções via stdin ou importe as funções diretamente.

Fase 6 tem dois scripts auxiliares: `arquivos_auxiliares/gerar_dados.py` regenera `dados_aurora_siger.csv` (seed fixo 42) e `arquivos_auxiliares/gerar_graficos.py` regenera o PNG em `graficos_ou_imagens/` (rode os dois de dentro de `fase6/`).

## Estrutura e convenções entre fases

- **Código oficial vs. individual.** O arquivo de entrada na raiz da fase (`code.py`, `main.py`, `codigo_fonte.py`) é a entrega do grupo. As pastas `fase1/Codes/`, `fase2/Codes/` e `fase3/code/<integrante>/` guardam versões individuais de cada integrante, mantidas como histórico: não são importadas pela entrega e não devem ser "sincronizadas" com ela.
- **Enunciado de cada fase.** `faseN/Referencias/solicitado.md` (fases 1–2) ou `faseN/referencias/instrucoes_faseN.md` (fases 3–4) contém o que o professor pediu. Leia antes de alterar uma entrega: os enunciados restringem a solução aos conteúdos estudados até aquela fase.
- **Restrições intencionais de implementação.** Várias escolhas que parecem reinvenção são requisito da disciplina: regressão linear por mínimos quadrados sem bibliotecas na fase 3, Bubble Sort e busca linear na fase 2, max-heap manual (heapify-up/down, sem `heapq`) e trie na fase 6, fases 4 e 5 em Python puro. Não substitua por bibliotecas.
- **Formato de entrega a partir da fase 4.** Arquivo único `codigo_fonte.py`, `link_video.txt` com o link do YouTube, relatório (`relatorio.pdf` ou `relatorio_tecnico.md`) e `README.md` próprio.
- **Continuidade de dados.** A fase 5 reaproveita os 13 módulos da fase 4 (mesmos nomes, tipos, consumo e prioridade operacional) em `fase5/dados_colonia.json`; mudanças nesses módulos devem permanecer coerentes entre as duas.
- **README raiz.** Ao concluir uma fase, o `README.md` da raiz ganha os badges de tecnologia, a entrada na árvore de estrutura e uma seção de resumo com links para o README e o relatório da fase.

## Detalhes por fase que não são óbvios

- **Fase 3** é a única modularizada: `main.py` orquestra `data/gerar.py` (365 dias simulados) → `src/energia.py` e `src/decisao.py` (classificação por registro, usando limiares e prioridades de `src/dados.py`) → `src/previsao.py` (regressão) → `src/relatorio.py` (saída). Os imports são absolutos a partir de `fase3/` (`from src.dados import ...`). O README cita um `graficos.py` que não existe; o gráfico é gerado por `referencias/img/gerar_img.py`.
- **Fase 5** grava em disco durante o uso: `dados_colonia.json` é reescrito ao cadastrar alertas e `registros_colonia.txt` recebe append a cada sessão/interação. Ambos são versionados, então rodar o sistema suja a árvore do git. Reverta antes de commitar, a menos que a mudança seja intencional. As duas formas (original e simplificada) de cada regra booleana ficam implementadas de propósito, para a prova por tabela-verdade.
- **Fase 4** exporta a rede para `rede_colonia_export.json` pelo menu; o arquivo versionado de referência é `arquivos_auxiliares/rede_colonia_dados.json`.
- **Fase 6**: registros cadastrados pelo menu valem só para a sessão (não são salvos no CSV).

## Git

Não há `.gitignore`, e `fase3/**/__pycache__/*.pyc` já está versionado. Não adicione novos `__pycache__`, ambientes virtuais ou `.ipynb_checkpoints` aos commits.
