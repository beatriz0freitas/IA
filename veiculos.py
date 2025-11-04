"""
Modelo de veículo (elétrico ou a combustão).
Contém propriedades de autonomia, consumo e custo por km.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Veiculo(ABC):
    id_veiculo: str
    posicao: str                            # localizacao atual
    autonomia_km: float                     # autonomia atual (km restantes)
    autonomiaMax_km: float                  # autonomia máxima
    capacidade_passageiros: int         
    custo_km: float                         # custo operacional (energia ou combustível)
    isDisponivel: bool = True               # disponibilidade do veículo
    km_total: float = 0.0                   # km totais percorridos

    # Verifica se o veículo pode percorrer determinada distância.
    def consegue_percorrer(self, distancia_km: float) -> bool:
        return self.autonomia_km >= distancia_km

    # Atualiza autonomia e posição após percorrer certa distância.
    def percorre(self, distancia_km: float, no_destino: str):
        self.autonomia_km = max(0.0, self.autonomia_km - distancia_km)
        self.posicao = no_destino
    
    @abstractmethod
    # Recarrega bateria ou reabastece tanque.
    def recarregar_reabastecer(self):
        pass

    @abstractmethod
    def tipo_veiculo(self) -> str:
        pass

@dataclass
class VeiculoConbustao(Veiculo):
    tempo_reabastecimento_min: int  
    emissao_C02_km: float   

    def recarregar_reabastecer(self):
        self.autonomia_km = self.autonomiaMax_km

    def tipo_veiculo(self) -> str:
        return "combustao"

    #todo: cálculo de emissões e custos adicionais.
    #todo: apenas reabastecer se estiver num nó com tipo "posto_abastecimento".
    #todo: custo
    #todo: reabastecimento nao ser total
    #todo: tempo de reabastecimento afetar a simulação

@dataclass
class VeiculoEletrico(Veiculo):
    tempo_recarregamento_min: int  
    capacidade_bateria_kWh: float    
    consumo_kWh_km: float

    def recarregar_reabastecer(self):
        self.autonomia_km = self.autonomiaMax_km

    def tipo_veiculo(self) -> str:
        return "eletrico"
    
    #todo: apenas recarregar se estiver num nó com tipo "estacao_recarga".
    #todo: custo
    #todo: carregamento nao ser total