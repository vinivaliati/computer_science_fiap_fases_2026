"""
arquitetura.py - relação do protótipo com arquitetura computacional e desempenho.
Mede, de verdade, a diferença entre um laço Python e uma operação vetorizada do NumPy.
"""
import time

import numpy as np


def benchmark(n=2_000_000):
    t = np.linspace(0, 24, n)
    inicio = time.perf_counter()
    soma = 0.0
    lista = t.tolist()
    for x in lista:
        soma += max(0.0, np.sin(np.pi * (x - 6) / 12)) if 6 <= x <= 18 else 0.0
    tempo_laco = time.perf_counter() - inicio
    inicio = time.perf_counter()
    soma_v = float(np.sum(np.where((t >= 6) & (t <= 18), np.sin(np.pi * (t - 6) / 12), 0.0)))
    tempo_vet = time.perf_counter() - inicio
    return tempo_laco, tempo_vet, soma, soma_v


def menu_arquitetura():
    print("\n  Medindo 2 milhões de pontos da curva de geração solar...")
    laco, vet, soma, soma_v = benchmark()
    print("  Laço em Python : %.3f s" % laco)
    print("  NumPy vetorizado: %.3f s  (%.0fx mais rápido, mesmo resultado: %.1f vs %.1f)" % (
        vet, laco / vet if vet else 0, soma, soma_v))
    print("""
  Como isso se relaciona com a colônia:
  - CPU: roda o menu, o banco e a lógica (poucos núcleos fortes, decisões sequenciais).
  - Vetorização/SIMD: o ganho acima vem de aplicar a mesma operação em vários dados de uma vez.
  - GPU: milhares de núcleos simples; ajudaria se simulássemos centenas de módulos/cenários em
    paralelo (cada cenário de tempestade é independente = paralelismo de dados).
  - NPU/TPU: aceleradores de baixo consumo para rodar modelos de IA (ex.: previsão de consumo)
    na própria colônia, onde cada watt importa e não dá para depender da Terra (atraso de 3 a 22 min).
  - Memória e largura de banda: nosso gargalo é mover dados (ler o banco, copiar arrays), não
    calcular. Manter os dados perto de quem calcula (cache/memória local) economiza energia.
  - Sustentabilidade: computação também consome energia; um modelo linear pequeno em CPU gasta
    muito menos que uma rede grande em GPU, e é suficiente para este problema.
  - Computação heterogênea/chiplets: combinar CPU + acelerador no mesmo pacote reduz a
    movimentação de dados e o consumo.""")
