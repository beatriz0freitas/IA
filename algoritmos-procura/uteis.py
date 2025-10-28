"""
Funções auxiliares comuns a vários algoritmos:
- Cálculo de distância euclidiana
- Funções de custo ou tempo estimado
- Outras heurísticas futuras
"""

import math
from models.graph import Node

"""Calcula a distância euclidiana (em km) entre dois nós."""
def euclidean_distance(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

""" Estima o tempo (em minutos) entre dois nós com base na distância euclidiana. """
def heuristic_time(a: Node, b: Node, avg_speed_kmh: float = 40.0) -> float:
    dist_km = euclidean_distance(a, b)
    if avg_speed_kmh <= 0:
        avg_speed_kmh = 40.0
    return (dist_km / avg_speed_kmh) * 60.0  # minutos
