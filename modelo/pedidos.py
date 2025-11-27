"""
Estrutura de um pedido de transporte.
Contém origem, destino, número de passageiros, prioridade e preferência ambiental.
"""

from dataclasses import dataclass
from typing import Literal
from enum import Enum
from typing import Optional

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
    prioridade: int                             # maior valor = mais urgente
    pref_ambiental: Literal["eletrico","combustao"]
    estado: EstadoPedido
    veiculo_atribuido: str                      # id do veículo atribuído ao pedido
    instante_atendimento: Optional[int] = None     
    tempo_max_espera: Optional[int] = None        # em minutos       

    # Validação automática da preferência ambiental.
    def __post_init__(self):
        if self.pref_ambiental not in ("eletrico", "combustao"):
            raise ValueError( f"Preferência ambiental inválida: {self.pref_ambiental}." "Deve ser 'eletrico' ou 'combustao'." )
        
        if self.passageiros <= 0:
            raise ValueError( f"Número de passageiros inválido, recebido: {self.passageiros}.")
        
        if self.prioridade < 0:
            raise ValueError(f"Prioridade deve ser >= 0, recebido: {self.prioridade}")
        
        if self.posicao_inicial == self.posicao_destino:
            raise ValueError(f"Origem e destino não podem ser iguais: {self.posicao_inicial}")
        
    # Valida se o pedido tem número válido de passageiros e validacao adicional em tempo de execucao
    def valida_pedido(self) -> bool:
        return self.passageiros > 0 and self.posicao_inicial != self.posicao_destino
              
    def atribui_veiculo_pedido(self, taxi_id: str):
        self.veiculo_atribuido = taxi_id
    
    # verifica se pedido expirou com base no tempo máximo de espera definido
    def expirou(self, tempo_atual: int) -> bool:
        if self.tempo_max_espera is None:
            return False
        
        return (tempo_atual - self.instante_pedido) > self.tempo_max_espera