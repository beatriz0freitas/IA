"""
Implementação do algoritmo Uniform Cost Search (UCS).
Procura não informada: expande o nó com menor custo acumulado (g).
"""

import heapq
from typing import Dict, List, Tuple, Optional
from modelo.grafo import Grafo


# Calcula o caminho de menor custo (tempo total em minutos) entre dois nós. Retorna: (custo_total_min, caminho)
def uniform_cost_search(graph: Grafo, start_id: str, goal_id: str) -> Tuple[float, List[str]]:
    if start_id == goal_id:
        return 0.0, [start_id]

    frontier = []
    heapq.heappush(frontier, (0.0, start_id))
    came_from: Dict[str, Optional[str]] = {start_id: None}
    cost_so_far: Dict[str, float] = {start_id: 0.0}

    while frontier:
        current_cost, current = heapq.heappop(frontier)

        if current == goal_id:
            # Reconstrução do caminho
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return cost_so_far[goal_id], list(reversed(path))

        for aresta in graph.vizinhos(current):
            vizinho = aresta.no_destino
            custo = aresta.tempo_real()  # Usa tempo considerando trânsito

            # Ignora arestas bloqueadas
            if custo == float('inf'):
                continue

            novo_custo = cost_so_far[current] + custo
            if vizinho not in cost_so_far or novo_custo < cost_so_far[vizinho]:
                cost_so_far[vizinho] = novo_custo
                came_from[vizinho] = current
                heapq.heappush(frontier, (novo_custo, vizinho))


    return float('inf'), []
