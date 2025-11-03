"""
Representação da cidade como grafo.
Cada nó é uma localização (zona, estação de recarga, posto de abastecimento, etc.).
Cada aresta tem distância e tempo associados.
"""

from dataclasses import dataclass
from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# um Node poderia ser tanto recolha de passageiros como posto de abastecimento nao?
@dataclass
class Node:
    id: str
    x: float
    y: float
    type: str  # "recolha de passageiros", "estação de recarga", "posto de abastecimento", etc.

@dataclass
class Edge:
    to_node: str
    distance_km: float
    travel_time_min: float
    # congestion: float # multiplier do tempo de travessia 0-1

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.adj: Dict[str, List[Edge]] = {}

    """Adiciona um nó ao grafo."""
    def add_node(self, node: Node):
        self.nodes[node.id] = node
        if node.id not in self.adj:
            self.adj[node.id] = []
    
    """Adiciona uma aresta bidirecional entre dois nós."""
    def add_edge(self, origin: str, dest: str, distance_km: float, travel_time_min: float):
        if origin not in self.nodes or dest not in self.nodes:
            raise ValueError("Nós devem ser adicionados antes das arestas.")
        self.adj[origin].append(Edge(dest, distance_km, travel_time_min))
        self.adj[dest].append(Edge(origin, distance_km, travel_time_min))

    """Devolve a aresta entre dois nodos, se existir."""
    def get_edge(self, src: str, dest: str) -> Edge:
        for e in self.adj[src]:
            if e.to_node == dest:
                return e
        raise ValueError(f"No edge from {src} to {dest}")

    """Retorna os vizinhos de um nó."""
    def neighbors(self, node_id: str) -> List[Edge]:
        return self.adj.get(node_id, [])

    """Procura BFS."""
    def bfs(self, start_id: str, goal_id: str) -> List[str]:
        if start_id not in self.nodes or goal_id not in self.nodes:
            raise ValueError("Nó inicial ou final não existe no grafo.")

        visited = set()
        queue = deque([(start_id, [start_id])])  # (nó atual, caminho até aqui)

        while queue:
            current, path = queue.popleft()

            if current == goal_id:
                # omitimos o nó inicial antes de retornar
                return path[1:]

            visited.add(current)

            for edge in self.neighbors(current):
                neighbor = edge.to_node
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    visited.add(neighbor)

        return []  # nenhum caminho encontrado
    
    """Procura DFS."""
    def dfs(self, start_id: str, goal_id: str) -> List[str]:
        if start_id not in self.nodes or goal_id not in self.nodes:
            raise ValueError("Nó inicial ou final não existe no grafo.")

        visited = set()
        stack = [(start_id, [start_id])]  # (current_node, path_so_far)

        while stack:
            current, path = stack.pop()
            if current == goal_id:
                return path

            if current not in visited:
                visited.add(current)
                for edge in self.neighbors(current):
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))

        return []

    # usar desenha("kk", False/True para mostrar tempos, escala à escolha)
    # o "kk" faz o grafico em escala com as distancias definidas
    def desenha(self, mode="coords", show_time=False, scale=1.0):
        """
        Args:
            mode: "coords" -> place nodes at (node.x, node.y) (visual edge length = geometric distance)
                "kk"     -> Kamada-Kawai layout using edge distance_km as target lengths
                "coords+kk" -> use node coords as initial positions, then run KK to match distance_km
            show_time: if True show travel_time_min labels; otherwise show distance_km
            scale: visual scale factor for coordinates or final layout
        """
        g = nx.Graph()

        # Add nodes with metadata
        for nid, node in self.nodes.items():
            g.add_node(nid, x=node.x, y=node.y, type=node.type)

        # Add edges and attach distance/time as attributes; avoid duplicating since graph is undirected
        for origin, edges in self.adj.items():
            for edge in edges:
                if g.has_edge(origin, edge.to_node):
                    continue
                g.add_edge(origin, edge.to_node,
                        distance=edge.distance_km,
                        time=edge.travel_time_min,
                        weight=edge.distance_km)  # weight used by KK

        # Choose layout
        pos = None
        if mode == "coords":
            # Use the node coordinates directly (scaled)
            pos = {nid: (data['x'] * scale, data['y'] * scale) for nid, data in g.nodes(data=True)}

        elif mode == "kk":
            # Kamada-Kawai trying to honor edge 'weight' as desired lengths
            # Lower weight -> closer nodes; KK uses 'weight' attribute by default if provided
            # We pass weight='weight' explicitly.
            pos = nx.kamada_kawai_layout(g, weight='weight', scale=scale)

        elif mode == "coords+kk":
            # Use coords as initial positions, then KK to better match distances.
            init_pos = {nid: (data['x'] * scale, data['y'] * scale) for nid, data in g.nodes(data=True)}
            # nx.kamada_kawai_layout accepts a 'pos' argument as initial guess
            pos = nx.kamada_kawai_layout(g, weight='weight', scale=scale, pos=init_pos)

        else:
            raise ValueError("mode must be one of: 'coords', 'kk', 'coords+kk'")

        # Draw nodes and labels
        nx.draw_networkx_nodes(g, pos, node_size=700, node_color='skyblue', edgecolors='black')
        nx.draw_networkx_labels(g, pos, font_weight='bold')

        # Draw edges
        nx.draw_networkx_edges(g, pos, width=2, alpha=0.8)

        # Edge labels: distance or time
        label_attr = 'time' if show_time else 'distance'
        labels = nx.get_edge_attributes(g, label_attr)
        # format labels
        edge_labels = {k: f"{v:.1f}" for k, v in labels.items()}
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_color='red')

        plt.axis('equal')
        plt.axis('off')
        plt.show()