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
    km_sem_passageiros: float               # km percorridos sem passageiros
    indice_rota: int                        # índice atual na rota
    tempo_ocupado_ate: int = 0              # tempo até ficar disponível (minutos simulação)
    id_pedido_atual: str = None             # id do pedido que está a servir atualmente
    rota: list[str] = None                  # rota atual (lista de nós)
           
    def consegue_percorrer(self, distancia_km: float) -> bool:
        return self.autonomia_km >= distancia_km
    
    def pode_transportar(self, num_passageiros: int) -> bool:
        return self.capacidade_passageiros >= num_passageiros

    # Atualiza a posição do veículo após percorrer uma distância. Também atualiza autonomia, km_total e regista debug da rota atual. 
    def move(self, distancia_km: float, no_destino: str, com_passageiros: bool = False):
        self.autonomia_km = max(0.0, self.autonomia_km - distancia_km)
        self.posicao = no_destino
        self.km_total += distancia_km

        if not com_passageiros:
            self.km_sem_passageiros += distancia_km

    def repor_autonomia(self, tipo_no:TipoNo, tempo_atual: int, recarga_parcial: float = 1.0):
        """
        Suporta recarga/reabastecimento parcial ou total.
        Retorna: (sucesso, custo_operacao, tempo_ocupacao)
        """
        if not self.pode_carregar_abastecer(tipo_no):
            return False, 0.0, 0

        capacidade_recarregar = (self.autonomiaMax_km - self.autonomia_km) * recarga_parcial
        self.autonomia_km = min(self.autonomiaMax_km, self.autonomia_km + capacidade_recarregar)

        if self.tipo_veiculo() == "eletrico":
            tempo_base = self.tempo_recarregamento_min
            self.estado = EstadoVeiculo.A_CARREGAR
            # Custo de recarga elétrica (€/kWh)
            kWh_necessarios = capacidade_recarregar * self.consumo_kWh_km
            custo_recarga = kWh_necessarios * 0.15  # €0.15 por kWh
        else:
            tempo_base = self.tempo_reabastecimento_min
            self.estado = EstadoVeiculo.A_ABASTECER
            # Custo de reabastecimento (mais caro)
            litros_necessarios = capacidade_recarregar * 0.08  # ~8L/100km
            custo_recarga = litros_necessarios * 1.6  # €1.60 por litro

        tempo_ocupacao = int(tempo_base * recarga_parcial)
        self.tempo_ocupado_ate = tempo_atual + tempo_ocupacao

        return True, custo_recarga, tempo_ocupacao
    
    def definir_rota(self, rota: list[str]):
        self.rota = rota
        self.indice_rota = 0

    # Move veículo um passo na rota com gestão correta de estados - Retorna: (moveu_com_sucesso, chegou_ao_destino)
    def mover_um_passo(self, grafo: Grafo, tempo_atual: int):

        if tempo_atual < self.tempo_ocupado_ate:
            return False, False
        
        if self.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER):
            self.estado = EstadoVeiculo.DISPONIVEL
            return False, False
        
        if not self.rota or self.indice_rota >= len(self.rota) - 1:
            return False, True  # Não moveu mas já está no destino
        
        prox_no = self.rota[self.indice_rota + 1]
        aresta = grafo.get_aresta(self.posicao, prox_no)

        # Determina se está com passageiros
        com_passageiros = (self.estado == EstadoVeiculo.A_SERVICO)

        self.move(aresta.distancia_km, prox_no, com_passageiros)
        self.indice_rota += 1

        # Define tempo ocupado até o veículo chegar ao próximo nó
        tempo_viagem = int(aresta.tempo_real())
        self.tempo_ocupado_ate = tempo_atual + tempo_viagem

        chegou = (self.indice_rota >= len(self.rota) - 1)

        return True, chegou
    
    def custo_operacao(self, distancia_km: float) -> float:
        """
        Calcula custo total de operação considerando:
        - Custo por km (energia/combustível)
        - Desgaste do veículo
        """
        custo_base = self.custo_km * distancia_km
        custo_desgaste = 0.02 * distancia_km  # Desgaste fixo por km
        return custo_base + custo_desgaste

    @abstractmethod
    def tipo_veiculo(self) -> str:
        pass

    @abstractmethod
    def pode_carregar_abastecer(self, tipo_no: TipoNo) -> bool:
        pass

    @abstractmethod
    def calcula_emissao(self, distancia_km: float) -> float:
        pass



@dataclass(kw_only=True)
class VeiculoCombustao(Veiculo):
    tempo_reabastecimento_min: int
    emissao_CO2_km: float

    def tipo_veiculo(self) -> str:
        return "combustao"

    def pode_carregar_abastecer(self, tipo_no: TipoNo) -> bool:
        return tipo_no == TipoNo.POSTO_ABASTECIMENTO

    def calcula_emissao(self, distancia_km: float) -> float:
        return max(0.0, distancia_km) * self.emissao_CO2_km

    def custo_operacao(self, distancia_km: float) -> float:
        """
        Custo de combustão inclui:
        - Custo de combustível (maior que elétrico)
        - Desgaste do motor (maior que elétrico)
        - Taxa ambiental (penalização por emissões)
        """
        custo_base = self.custo_km * distancia_km
        custo_desgaste = 0.03 * distancia_km  # Maior desgaste que elétrico
        taxa_ambiental = self.emissao_CO2_km * distancia_km * 0.5  # Taxa por CO2
        return custo_base + custo_desgaste + taxa_ambiental

@dataclass(kw_only=True)
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

    def custo_operacao(self, distancia_km: float) -> float:
        """
        Custo elétrico inclui:
        - Custo de energia (mais barato que combustível)
        - Desgaste reduzido (motores elétricos têm menos desgaste)
        - Bónus ambiental (incentivo para veículos limpos)
        """
        custo_base = self.custo_km * distancia_km
        custo_desgaste = 0.01 * distancia_km  # Menor desgaste
        bonus_ambiental = -0.02 * distancia_km  # Incentivo verde
        return max(0.0, custo_base + custo_desgaste + bonus_ambiental)