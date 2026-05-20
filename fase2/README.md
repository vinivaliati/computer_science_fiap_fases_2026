# Aurora Siger — MGPEB (Módulo de Gerenciamento de Pouso)

Simulação de um sistema de gerenciamento de pouso para a missão Aurora Siger, utilizando estruturas de dados, algoritmos clássicos e lógica booleana para tomada de decisão em um ambiente crítico.

---

## Organização

    fase2/
    ├── codes/           # código de cada integrante
    ├── referencias/     # arquivos, exemplos e imagens de referência
    └── relatorio.pdf    # relatório final

---

## O que o notebook faz

- Gera módulos de pouso simulados  
- Organiza os módulos em uma fila de chegada  
- Aplica algoritmos de busca (menor combustível, maior prioridade)  
- Reordena a fila em situações críticas utilizando Bubble Sort  
- Simula decisões de pouso com base em regras booleanas  
- Classifica cada módulo como:
  - POUSADO
  - ESPERA
  - ALERTA

---

## Regras de Decisão

O sistema considera as seguintes condições:

| Condição | Descrição |
|----------|----------|
| combustível | nível disponível para pouso |
| atmosfera | condições favoráveis |
| área de pouso | disponibilidade |
| sensores | funcionamento correto |

### Lógica aplicada:

- Pouso ocorre apenas se sensores e área estiverem OK  
- Em condições normais, segue a ordem de chegada (FIFO)  
- Em caso de combustível crítico, módulos prioritários podem ser antecipados  
- Situações de risco são classificadas como alerta  

---

## Estruturas Utilizadas

- Lista → representação da fila de módulos  
- Busca linear → identificação de módulos específicos  
- Bubble Sort → ordenação por prioridade em cenários críticos  
- Condicionais (if/elif/else) → simulação da lógica de decisão  

---

## Modelagem Matemática

O projeto inclui a modelagem do consumo de combustível ao longo do tempo utilizando uma função exponencial, permitindo analisar situações de risco e apoiar decisões de pouso.

---

## Como rodar

1. Clone o repositório

    git clone https://github.com/vinivaliati/computer_science_fiap/tree/main/fase2  
    cd seu-repositorio/fase2

2. Crie e ative o ambiente virtual

    # Windows  
    python -m venv venv  
    venv\Scripts\activate  

    # Mac/Linux  
    python -m venv venv  
    source venv/bin/activate  

3. Instale as dependências

    pip install -r requirements.txt  

4. Execute o código

    python seu_script.py  

ou abra no notebook:

    jupyter notebook  

---

## Dependências

    random  
    numpy  
    matplotlib  

