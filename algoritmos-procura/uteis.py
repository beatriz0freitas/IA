"""
Funções auxiliares comuns a vários algoritmos:
- Cálculo de distância euclidiana
- Funções de custo ou tempo estimado
- Outras heurísticas futuras
"""

import math
from models.graph import No

# Calcula a distância euclidiana (em km) entre dois nós.
def dist_euclidiana(no_a: No, no_b: No) -> float:
    return math.hypot(no_a.x - no_b.x, no_a.y - no_b.y)

# Estima o tempo (em minutos) entre dois nós com base na distância euclidiana.
def tempo_heuristica(no_a: No, no_b: No,
                     velocidadeMedia_kmh: float = 40.0) -> float:
    dist_km = dist_euclidiana(no_a, no_b)
    if velocidadeMedia_kmh <= 0:
        velocidadeMedia_kmh = 40.0
    return (dist_km / velocidadeMedia_kmh) * 60.0  # minutos