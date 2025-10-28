"""
Implementação do algoritmo A* (A-estrela) para encontrar o caminho ótimo
entre dois nós do grafo.
"""

import heapq
from typing import Dict, List, Tuple, Optional
from models.graph import Graph
from algorithms.utils import euclidean_distance

"""
Calcula o menor custo (tempo em minutos) e o caminho entre dois nós.
Retorna (tempo_total_min, [lista_de_nós]).
"""
def a_star_search(graph: Graph, start_id: str, goal_id: str) -> Tuple[float, List[str]]:
    if start_id == goal_id:
        return 0.0, [start_id]

    open_set = []
    heapq.heappush(open_set, (0.0, start_id))
    came_from: Dict[str, Optional[str]] = {start_id: None}
    g_score: Dict[str, float] = {start_id: 0.0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal_id:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return g_score[goal_id], list(reversed(path))

        for edge in graph.neighbors(current):
            tentative_g = g_score[current] + edge.travel_time_min
            if edge.to_node not in g_score or tentative_g < g_score[edge.to_node]:
                came_from[edge.to_node] = current
                g_score[edge.to_node] = tentative_g
                # heurística importada do módulo utils
                h = euclidean_distance(graph.nodes[edge.to_node], graph.nodes[goal_id])
                f = tentative_g + h
                heapq.heappush(open_set, (f, edge.to_node))

    return float('inf'), []
