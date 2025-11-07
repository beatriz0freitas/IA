"""
Modelo de veículo (elétrico ou a combustão).
Contém propriedades de autonomia, consumo e custo por km.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from modelo.grafo import Grafo, TipoNo

class EstadoVeiculo(Enum):
    DISPONIVEL = "disponivel"         
    A_SERVICO = "a_servico"           # a transportar passageiros
    A_CARREGAR = "recarregando"       
    A_ABASTECER = "reabastecendo"   
    INDISPONIVEL = "indisponivel"     # manutenção, fora de serviço
    EM_DESLOCACAO = "deslocando"         # em movimento sem passageiro

@dataclass
class Veiculo(ABC):
    id_veiculo: str
    posicao: str                            # localizacao atual
    autonomia_km: float                     # autonomia atual (km restantes)
    autonomiaMax_km: float                  # autonomia máxima
    capacidade_passageiros: int         
    custo_km: float                         # custo operacional (energia ou combustível)
    estado: EstadoVeiculo
    km_total: float                         # km totais percorridos
    rota: list[str] = None                  # rota atual (lista de nós)
    indice_rota: int = 0                  

    def consegue_percorrer(self, distancia_km: float) -> bool:
        return self.autonomia_km >= distancia_km
    
    def pode_transportar(self, num_passageiros: int) -> bool:
        return self.capacidade_passageiros >= num_passageiros

    # Move o veículo: atualiza autonomia, posição e km_total. - o tempo de deslocação e a validação de existência de aresta/rota são responsabilidade do gestor/graph.
    def move(self, distancia_km: float, no_destino: str):
        self.autonomia_km = max(0.0, self.autonomia_km - distancia_km)
        self.posicao = no_destino
        self.km_total += distancia_km

    # Recarrega/reabastece o veículo se estiver no tipo de nó correto
    def repor_autonomia(self, tipo_no:TipoNo):
        if self.pode_carregar_abastecer(tipo_no):
            self.autonomia_km = self.autonomiaMax_km
            self.estado = EstadoVeiculo.DISPONIVEL
            return True
        return False
    
    def definir_rota(self, rota: list[str]):
        self.rota = rota
        self.indice_rota = 0
    
    #todo: considerar meter no gestor de frota
    def mover_um_passo(self, grafo: Grafo):
        if not self.rota or self.indice_rota >= len(self.rota) - 1:
            return False
        prox_no = self.rota[self.indice_rota + 1]
        aresta = grafo.get_aresta(self.posicao, prox_no)
        self.move(aresta.distancia_km, prox_no)
        self.indice_rota += 1
        return True
    
    #todo: verifiar todas variaveis que influenciam custp
    def custo_operacao(self, distancia_km: float) -> float:
        return self.custo_km * distancia_km

    @abstractmethod
    def tipo_veiculo(self) -> str:
        pass

    @abstractmethod
    def pode_carregar_abastecer(self, tipo_no: TipoNo) -> bool:
        pass

    @abstractmethod
    def calcula_emissao(self, distancia_km: float) -> float:
        pass



@dataclass
class VeiculoCombustao(Veiculo):
    tempo_reabastecimento_min: int              
    emissao_CO2_km: float   

    def tipo_veiculo(self) -> str:
        return "combustao"

    def pode_carregar_abastecer(self, tipo_no: TipoNo) -> bool:
        return tipo_no == TipoNo.POSTO_ABASTECIMENTO
    
    def calcula_emissao(self, distancia_km: float) -> float:
        return max(0.0, distancia_km) * self.emissao_CO2_km

    #todo: custos
    #todo: reabastecimento nao ser total
    #todo: tempo de reabastecimento afetar a simulação

@dataclass
class VeiculoEletrico(Veiculo):
    tempo_recarregamento_min: int  
    capacidade_bateria_kWh: float    
    consumo_kWh_km: float

    def tipo_veiculo(self) -> str:
        return "eletrico"
    
    def pode_carregar_abastecer(self, tipo_no):
        return tipo_no == TipoNo.ESTACAO_RECARGA
    
    def calcula_emissao(self, distancia_km: float) -> float:
        return 0.0

    #todo: custo
    #todo: carregamento nao ser total