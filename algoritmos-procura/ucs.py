"""
Implementação do algoritmo Uniform Cost Search (UCS).
Procura não informada: expande o nó com menor custo acumulado (g).
"""

import heapq
from typing import Dict, List, Tuple, Optional
from models.graph import Graph

"""
Calcula o caminho de menor custo (tempo total em minutos) entre dois nós.
Retorna: (custo_total_min, caminho)
"""
def uniform_cost_search(graph: Graph, start_id: str, goal_id: str) -> Tuple[float, List[str]]:
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

        for edge in graph.neighbors(current):
            new_cost = cost_so_far[current] + edge.travel_time_min
            if edge.to_node not in cost_so_far or new_cost < cost_so_far[edge.to_node]:
                cost_so_far[edge.to_node] = new_cost
                came_from[edge.to_node] = current
                heapq.heappush(frontier, (new_cost, edge.to_node))

    return float('inf'), []
