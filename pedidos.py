"""
Estrutura de um pedido de transporte.
Contém origem, destino, número de passageiros, prioridade e preferência ambiental.
"""

from dataclasses import dataclass
from typing import Literal
from enum import Enum

class EstadoPedido(Enum):
    PENDENTE = "pendente"
    ATRIBUIDO = "atribuido"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    REJEITADO = "rejeitado"


@dataclass
class Pedido:
    id_pedido: str
    posicao_inicial: str
    posicao_destino: str
    passageiros: int
    instante_pedido: int                        # instante em minutos na simulação
    instante_atendimento: int               
    prioridade: int = 0                         # maior valor = mais urgente
    pref_ambiental: Literal["eletrico","combustao"]
    estado: EstadoPedido
    veiculo_atribuido: str                      # id do veículo atribuído ao pedido

    # Validação automática da preferência ambiental.
    def __post_init__(self):
        if self.pref_ambiental not in ("eletricop", "combustao"):
            raise ValueError(
                f"Preferência ambiental inválida: {self.pref_ambiental}. "
                "Deve ser 'eletrico' ou 'combustao'."
            )
    
    # Valida se o pedido tem número válido de passageiros.
    def valida_pedido(self) -> bool:
        return self.passageiros > 0 
    
