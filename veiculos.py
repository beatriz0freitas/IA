"""
Modelo de veículo (elétrico ou a combustão).
Contém propriedades de autonomia, consumo e custo por km.
"""
from typing import List
from dataclasses import dataclass, field
from collections import deque
from typing import Deque

def get_frota():
    res = dict()
    newTaxi = Vehicle(1, "K", False, 200.0, 600.0, 4, 6.2)
    res.update({1: newTaxi})
    # adicionar frota...
    return res

@dataclass
class Vehicle:
    id: str
    position: str                               # localizacao atual
    is_electric: bool
    autonomy_km: float                          # autonomia atual (km restantes)
    autonomy_max_km: float                      # autonomia máxima
    passenger_capacity: int
    cost_per_km: float                          # custo operacional (energia ou combustível)
    available: bool = True                      # disponibilidade do veículo
    path: Deque[str] = field(default_factory=deque)  # rota a tomar pelo táxi

    """Atribui o id de um pedido ao táxi."""
    def assign_request(self, id: str):
        self.assigned_request = id
        return

    """Verifica se o veículo pode percorrer determinada distância."""
    def can_reach(self, distance_km: float) -> bool:
        return self.autonomy_km >= distance_km

    """Devolve o node seguinte na rota tomada."""
    def get_next_path_node(self):
        nextNodeId = self.path.popleft()
        if not self.path: # empty
            self.available = True
        return nextNodeId

    """Move-se para o próximo Node na rota definida."""
    def move(self, distance_km: float, nodeName: str):
        if self.can_reach(distance_km):
            self.autonomy_km = self.autonomy_km - distance_km
            self.position = nodeName
            #return self.available
            # retornar availability para trocar de frotaOcupada para frotaLivre(?)
        else:
            raise(ValueError("Autonomia insuficiente."))

    def set_path(self, path):
        self.path = deque(path)
        self.available = False
        return

    """Recarrega bateria ou reabastece tanque."""
    def recharge_or_refuel(self):
        self.autonomy_km = self.autonomy_max_km

    """Cálculo do custo de operação."""
    def operating_cost(self, distance_km: float) -> float:
        return self.cost_per_km * distance_km
