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
    priority: int = 0            # maior valor = mais urgente
    environmental_preference: Literal["eletrico","combustao"]
