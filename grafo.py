"""
Representação da cidade como grafo.
Cada nó é uma localização (zona, estação de recarga, posto de abastecimento, etc.).
Cada aresta tem distância e tempo associados.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class TipoNo(Enum):
    RECOLHA_PASSAGEIROS = "recolha de passageiros"
    ESTACAO_RECARGA = "estação de recarga"
    POSTO_ABASTECIMENTO = "posto de abastecimento"

@dataclass
class No:
    id_no: str
    posicaox: float
    posicaoy: float
    tipo: TipoNo          

@dataclass
class Aresta:
    no_destino: str
    distancia_km: float
    tempoViagem_min: float

class Graph:
    def __init__(self):
        self.nos: Dict[str, No] = {}
        self.adjacentes: Dict[str, List[Aresta]] = {}

    # Adiciona um nó ao grafo
    def adiciona_no(self, no: No):
        self.nos[no.id_no] = no
        if no.id_no not in self.adjacentes:
            self.adjacentes[no.id_no] = []
    
    # Adiciona uma aresta bidirecional entre dois nós.
    def adiciona_aresta(self, no_origem: str, no_destino: str, 
                              distancia_km: float, tempoViagem_min: float):
        if no_origem not in self.nos or no_destino not in self.nos:
            raise ValueError("Nós devem ser adicionados antes das arestas.")
        self.adjacentes[no_origem].append(Aresta(no_destino, distancia_km, tempoViagem_min))
        self.adjacentes[no_destino].append(Aresta(no_origem, distancia_km, tempoViagem_min))

    # Retorna os vizinhos de um nó.
    def vizinhos(self, id_no: str) -> List[Aresta]:
        return self.adjacentes.get(id_no, [])

    # Retorna a distância entre dois nós conectados.
    def distancia(self, origem: str, destino: str) -> float:
        for aresta in self.adjacentes.get(origem, []):
            if aresta.no_destino == destino:
                return aresta.distancia_km
        raise ValueError(f"Nós {origem} e {destino} não estão conectados.")