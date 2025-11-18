"""
A* (A-Estrela) refatorizado - Busca informada com heurística euclidiana
"""

import heapq
from typing import Dict, List, Tuple, Optional
from modelo.grafo import Grafo
from gestao.algoritmos_procura.uteis import dist_euclidiana


def a_star_search(
    grafo: Grafo, start_id: str, goal_id: str
) -> Tuple[float, List[str]]:
    """
    Encontra o caminho de menor custo entre dois nós usando A*.
    
    Retorna: (tempo_total_minutos, [lista_de_nós])
    """
    if start_id == goal_id:
        return 0.0, [start_id]

    if start_id not in grafo.nos or goal_id not in grafo.nos:
        raise ValueError(f"Nó inicial ou final não existe no grafo")

    open_set = []
    heapq.heappush(open_set, (0.0, start_id))

    came_from: Dict[str, Optional[str]] = {start_id: None}
    g_score: Dict[str, float] = {start_id: 0.0}
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        if current == goal_id:
            # Reconstruir caminho
            path = []
            node = goal_id
            while node is not None:
                path.append(node)
                node = came_from[node]
            return g_score[goal_id], list(reversed(path))

        closed_set.add(current)

        # Explorar vizinhos
        for aresta in grafo.vizinhos(current):
            vizinho = aresta.no_destino

            if vizinho in closed_set:
                continue

            # Custo real do deslocamento atual
            tentative_g = g_score[current] + aresta.tempoViagem_min

            # Se já foi visitado com custo menor, pular
            if vizinho in g_score and tentative_g >= g_score[vizinho]:
                continue

            # Atualizar scores
            came_from[vizinho] = current
            g_score[vizinho] = tentative_g

            # Calcular heurística (distância euclidiana até goal)
            h = dist_euclidiana(grafo.nos[vizinho], grafo.nos[goal_id])

            # f = g + h (custo real + estimado)
            f = tentative_g + h

            heapq.heappush(open_set, (f, vizinho))

    # Sem caminho encontrado
    return float('inf'), []