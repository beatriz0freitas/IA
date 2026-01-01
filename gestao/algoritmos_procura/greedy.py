"""
Greedy Best-First Search (puramente guloso): escolhe sempre o nó com menor
heurística ao objetivo. Não usa custo acumulado para tomar decisões.

Retorna (tempo_total_min, [lista_de_nós]).
"""

import heapq
from typing import Dict, List, Tuple, Optional
from modelo.grafo import Grafo
from gestao.algoritmos_procura.uteis import dist_euclidiana


def greedy(grafo: Grafo, start_id: str, goal_id: str) -> Tuple[float, List[str]]:
    if start_id == goal_id:
        return 0.0, [start_id]

    # heap de (h, node_id)
    open_set: List[Tuple[float, str]] = []
    heapq.heappush(open_set, (dist_euclidiana(grafo.nos[start_id], grafo.nos[goal_id]), start_id))

    came_from: Dict[str, Optional[str]] = {start_id: None}
    visited: set[str] = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal_id:
            # reconstruir caminho
            path: List[str] = []
            node: Optional[str] = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            # calcular tempo total percorrendo o caminho encontrado
            tempo_total = 0.0
            for a, b in zip(path, path[1:]):
                custo_ab = _tempo_aresta(grafo, a, b)
                if custo_ab == float("inf"):
                    return float("inf"), []  # caminho inválido (arestas bloqueadas a meio)
                tempo_total += custo_ab

            return tempo_total, path

        for aresta in grafo.vizinhos(current):
            no_destino = aresta.no_destino
            custo = aresta.tempo_real()

            # ignora arestas bloqueadas
            if custo == float("inf"):
                continue

            if no_destino in visited:
                continue

            # não "relaxa": primeira vez que encontro, fica
            if no_destino not in came_from:
                came_from[no_destino] = current

            h = dist_euclidiana(grafo.nos[no_destino], grafo.nos[goal_id])
            heapq.heappush(open_set, (h, no_destino))

    return float("inf"), []


def _tempo_aresta(grafo: Grafo, a: str, b: str) -> float:
    """
    Devolve o tempo_real da aresta entre a e b num grafo não dirigido.
    Procura em ambos os sentidos.
    """
    # procurar a -> b
    for aresta in grafo.vizinhos(a):
        if aresta.no_destino == b:
            return aresta.tempo_real()

    return float("inf")
