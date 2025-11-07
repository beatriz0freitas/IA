from collections import deque
from typing import List
from modelo.grafo import Grafo

# Procura em largura (BFS) entre dois nós do grafo.
def bfs(grafo: Grafo, start_id: str, goal_id: str) -> List[str]:
    if start_id not in grafo.nos or goal_id not in grafo.nos:
        raise ValueError("Nó inicial ou final não existe no grafo.")

    visitados = set()
    fila = deque([(start_id, [start_id])])  # (nó atual, caminho até aqui)

    while fila:
        atual, caminho = fila.popleft()
        if atual == goal_id:
            return caminho  # devolve caminho completo

        visitados.add(atual)
        for aresta in grafo.vizinhos(atual):
            vizinho = aresta.no_destino
            if vizinho not in visitados:
                fila.append((vizinho, caminho + [vizinho]))
                visitados.add(vizinho)

    return []  # nenhum caminho encontrado

# Procura BFS com passagem obrigatória por um checkpoint.
def bfs_com_checkpoint(grafo: Grafo, start_id: str, checkpoint_id: str, goal_id: str) -> List[str]:
    if (start_id not in grafo.nos or checkpoint_id not in grafo.nos or goal_id not in grafo.nos ):
        raise ValueError("Nó inicial, checkpoint ou final não existe no grafo.")

    caminho1 = bfs(grafo, start_id, checkpoint_id)
    caminho2 = bfs(grafo, checkpoint_id, goal_id)

    if not caminho1 or not caminho2:
        return []

    # Junta os dois caminhos, evitando repetir o checkpoint
    return caminho1 + caminho2[1:]
