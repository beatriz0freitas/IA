"""
Estrutura de um pedido de transporte.
Contém origem, destino, número de passageiros, prioridade e preferência ambiental.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Request:
    id: str
    origin: str
    destination: str
    passengers: int
    time_request: int        # instante em minutos na simulação
    priority: int = 0        # maior valor = mais urgente
    pref_environmental: Optional[str] = None  # 'electric' ou None
