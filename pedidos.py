"""
Estrutura de um pedido de transporte.
Contém origem, destino, número de passageiros, prioridade e preferência ambiental.
"""

from dataclasses import dataclass
from typing import Literal

@dataclass
class Request:
    id: str
    origin_position: str
    destination_position: str
    passengers: int
    schedule_request: int        # instante em minutos na simulação
    environmental_preference: Literal["eletrico","combustao"]
    priority: int = 0            # menor valor = maior prioridade, mesmo conceito mas invertido para negativos
                                 # porque python so te dá minheaps por default
    assigned_taxi_id: str = ""   # id do táxi a cargo do pedido

    """Validação automática da preferência ambiental."""
    def __post_init__(self):
        if self.environmental_preference not in ("eletrico", "combustao"):
            raise ValueError(
                f"Preferência ambiental inválida: {self.environmental_preference}. "
                "Deve ser 'electrico' ou 'combustao'."
            )
        
    """Atribui o ID do taxi encarregue do pedido."""
    def assign_taxi(self, taxi_id: str):
        self.assigned_taxi_id = taxi_id