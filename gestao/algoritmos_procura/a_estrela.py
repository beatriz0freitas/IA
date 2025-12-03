"""
Implementação do algoritmo A* (A-estrela) para encontrar o caminho ótimo
entre dois nós do grafo.
"""

import heapq
from . import uteis
from typing import Dict, List, Tuple, Optional
from modelo.grafo import Grafo
from gestao.algoritmos_procura.uteis import dist_euclidiana

# Calcula o menor custo (tempo em minutos) e o caminho entre dois nós. Retorna (tempo_total_min, [lista_de_nós]).
def a_star_search(grafo: Grafo, start_id: str, goal_id: str) -> Tuple[float, List[str]]:
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

        
        for aresta in grafo.vizinhos(current):
            no_destino = aresta.no_destino
            custo = aresta.tempo_real()  # Usa tempo considerando trânsito

            # Ignora arestas bloqueadas
            if custo == float('inf'):
                continue

            tentative_g = g_score[current] + custo

            if no_destino not in g_score or tentative_g < g_score[no_destino]:
                came_from[no_destino] = current
                g_score[no_destino] = tentative_g
                h = dist_euclidiana(grafo.nos[aresta.no_destino], grafo.nos[goal_id])
                f = tentative_g + h
                heapq.heappush(open_set, (f, no_destino))

    return float('inf'), []
