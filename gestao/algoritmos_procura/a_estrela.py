"""
Implementação do algoritmo A* (A-estrela) para encontrar o caminho ótimo
entre dois nós do grafo.
"""

import heapq
from .uteis import dist_euclidiana, heuristica_avancada
from typing import Dict, List, Tuple, Optional
from modelo.grafo import Grafo

def a_star_search(grafo: Grafo, start_id: str, goal_id: str, 
                  veiculo=None, tempo_atual=0, usar_heuristica_avancada=True) -> Tuple[float, List[str]]:
    """
    Algoritmo A* com opção de heurística avançada.
    
    Args:
        grafo: Grafo da cidade
        start_id: Nó de origem
        goal_id: Nó de destino
        veiculo: (Opcional) Veículo para considerar autonomia
        tempo_atual: (Opcional) Tempo atual para estimar trânsito
        usar_heuristica_avancada: Se True, usa heurística que considera autonomia e trânsito
    
    Returns:
        (custo_total, caminho)
    """
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
            custo = aresta.tempo_real()  # Considera trânsito

            # Ignora arestas bloqueadas
            if custo == float('inf'):
                continue

            tentative_g = g_score[current] + custo

            if no_destino not in g_score or tentative_g < g_score[no_destino]:
                came_from[no_destino] = current
                g_score[no_destino] = tentative_g
                
                # Escolha de heurística
                if usar_heuristica_avancada and veiculo is not None:
                    h = heuristica_avancada(grafo, veiculo, no_destino, goal_id, tempo_atual)
                else:
                    # Heurística simples (euclidiana)
                    h = dist_euclidiana(grafo.nos[no_destino], grafo.nos[goal_id])
                
                f = tentative_g + h
                heapq.heappush(open_set, (f, no_destino))

    return float('inf'), []