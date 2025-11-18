"""
Representação da cidade como grafo - CORRIGIDO
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


class Grafo:
    def __init__(self):
        self.nos: Dict[str, No] = {}
        self.adjacentes: Dict[str, List[Aresta]] = {}

    def adiciona_no(self, no: No):
        if no.id_no not in self.nos:
            self.nos[no.id_no] = no
            self.adjacentes[no.id_no] = []

    def get_no(self, id_no: str) -> No:
        return self.nos[id_no]

    def adiciona_aresta(
        self, no_origem: str, no_destino: str,
        distancia_km: float, tempoViagem_min: float
    ):
        if no_origem not in self.nos or no_destino not in self.nos:
            raise ValueError("Nós devem ser adicionados antes das arestas.")
        self.adjacentes[no_origem].append(
            Aresta(no_destino, distancia_km, tempoViagem_min)
        )
        self.adjacentes[no_destino].append(
            Aresta(no_origem, distancia_km, tempoViagem_min)
        )

    def get_aresta(self, no_origem: str, no_dest: str) -> Aresta:
        """Devolve a aresta entre dois nodos, se existir."""
        # ✓ CORREÇÃO: Se nós são iguais, retorna aresta com distância 0
        if no_origem == no_dest:
            return Aresta(no_dest, 0.0, 0.0)
        
        for e in self.adjacentes[no_origem]:
            if e.no_destino == no_dest:
                return e
        raise ValueError(f"Não existe aresta de {no_origem} para {no_dest}")

    def vizinhos(self, id_no: str) -> List[Aresta]:
        return self.adjacentes.get(id_no, [])

    def distancia(self, origem: str, destino: str) -> float:
        """
        Retorna a distância entre dois nós conectados.
        CORRIGIDO: Se origem == destino, retorna 0 em vez de erro
        """
        # ✓ CORREÇÃO: Se nós são iguais, distância é 0
        if origem == destino:
            return 0.0

        for aresta in self.adjacentes.get(origem, []):
            if aresta.no_destino == destino:
                return aresta.distancia_km

        raise ValueError(
            f"Nós {origem} e {destino} não estão conectados."
        )