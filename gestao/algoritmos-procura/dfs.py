from typing import List
from modelo.grafo import Grafo

# Procura em profundidade (DFS) no grafo. - Retorna o caminho encontrado (não necessariamente o mais curto).
def dfs(grafo: Grafo, start_id: str, goal_id: str) -> List[str]:
    if start_id not in grafo.nos or goal_id not in grafo.nos:
        raise ValueError("Nó inicial ou final não existe no grafo.")

    visitados = set()
    pilha = [(start_id, [start_id])]  # (nó atual, caminho até aqui)

    while pilha:
        atual, caminho = pilha.pop()
        if atual == goal_id:
            return caminho

        if atual not in visitados:
            visitados.add(atual)
            for aresta in grafo.vizinhos(atual):
                vizinho = aresta.no_destino
                if vizinho not in visitados:
                    pilha.append((vizinho, caminho + [vizinho]))

    return []  # nenhum caminho encontrado
