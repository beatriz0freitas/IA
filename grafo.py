"""
Representação da cidade como grafo.
Cada nó é uma localização (zona, estação de recarga, posto de abastecimento, etc.).
Cada aresta tem distância e tempo associados.
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Node:
    id: str
    x: float
    y: float
    type: str  # 'pickup', 'dropoff', 'charge', 'fuel', etc.

@dataclass
class Edge:
    to_node: str
    distance_km: float
    travel_time_min: float

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

    """Retorna os vizinhos de um nó."""
    def neighbors(self, node_id: str) -> List[Edge]:
        return self.adj.get(node_id, [])
