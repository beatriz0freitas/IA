"""
Função de custo composta que pondera múltiplos objetivos:
- Tempo de resposta
- Custo operacional
- Emissões ambientais
- Penalização por rejeição
"""

from dataclasses import dataclass
from typing import List
from modelo.veiculos import Veiculo
from modelo.pedidos import Pedido


@dataclass
class PesosCusto:
    """
    Pesos para função de custo composta.
    
    Justificação dos valores padrão:
    - 0.4: Tempo é prioritário (satisfação do cliente)
    - 0.3: Custo importante mas secundário
    - 0.2: Sustentabilidade relevante
    - 0.1: Rejeição deve ser evitada mas é menos frequente
    
    Total = 1.0 (normalizado)
    """
    tempo: float = 0.4      # α - Peso do tempo de resposta
    custo: float = 0.3      # β - Peso do custo operacional
    emissao: float = 0.2    # γ - Peso das emissões
    rejeicao: float = 0.1   # δ - Peso de rejeições


class FuncaoCustoComposta:
    """
    Calcula custo composto considerando múltiplos objetivos.
    """
    
    def __init__(self, pesos: PesosCusto = None):
        self.pesos = pesos or PesosCusto()
        
        # Fatores de normalização (estimados para tornar valores comparáveis)
        self.NORM_TEMPO = 60.0        # Tempo típico: 60 min
        self.NORM_CUSTO = 50.0        # Custo típico: €50
        self.NORM_EMISSAO = 5.0       # Emissão típica: 5 kg CO2
        self.NORM_PENALIZACAO = 100.0 # Penalização por rejeição: €100
    
    def calcular_custo_atribuicao(self, veiculo: Veiculo, pedido: Pedido, 
                                   tempo_resposta: float, distancia_total: float) -> float:
        """
        Calcula custo composto de atribuir um veículo a um pedido.
        
        Args:
            veiculo: Veículo a atribuir
            pedido: Pedido a atender
            tempo_resposta: Tempo desde pedido até início de serviço (min)
            distancia_total: Distância total da operação (km)
        
        Returns:
            Custo composto normalizado
        """
        # Componentes (normalizadas)
        custo_tempo_norm = (tempo_resposta / self.NORM_TEMPO)
        
        custo_operacional = veiculo.custo_operacao(distancia_total)
        custo_operacional_norm = (custo_operacional / self.NORM_CUSTO)
        
        emissoes = veiculo.calcula_emissao(distancia_total)
        custo_emissao_norm = (emissoes / self.NORM_EMISSAO)
        
        # Penalização por prioridade não atendida
        # Pedidos de alta prioridade que demoram muito são penalizados
        penalizacao_prioridade = 0.0
        if pedido.prioridade >= 3 and tempo_resposta > 10:
            penalizacao_prioridade = 0.5  # Penalização adicional
        
        # Custo total ponderado
        custo_total = (
            self.pesos.tempo * custo_tempo_norm +
            self.pesos.custo * custo_operacional_norm +
            self.pesos.emissao * custo_emissao_norm +
            penalizacao_prioridade
        )
        
        return custo_total
    
    def calcular_custo_rejeicao(self, pedido: Pedido) -> float:
        """
        Calcula penalização por rejeitar um pedido.
        
        Pedidos de alta prioridade têm penalização maior.
        """
        penalizacao_base = 1.0  # Custo normalizado base
        
        # Multiplica pela prioridade
        penalizacao = penalizacao_base * (1 + pedido.prioridade * 0.5)
        
        return self.pesos.rejeicao * penalizacao
    
    def calcular_custo_estado_global(self, metricas: dict) -> float:
        """
        Calcula custo de um estado global da simulação.
        
        Usado para avaliar qualidade geral da solução.
        """
        tempo_medio = metricas.get("tempo_medio_resposta", 0)
        custo_total = metricas.get("custo_total", 0)
        emissoes_total = metricas.get("emissoes_totais", 0)
        pedidos_rejeitados = metricas.get("pedidos_rejeitados", 0)
        
        # Normaliza
        custo_tempo_norm = tempo_medio / self.NORM_TEMPO
        custo_ops_norm = custo_total / (self.NORM_CUSTO * 10)  # Assumindo ~10 pedidos
        custo_emissao_norm = emissoes_total / (self.NORM_EMISSAO * 10)
        custo_rejeicao_norm = pedidos_rejeitados  # Já é contagem
        
        return (
            self.pesos.tempo * custo_tempo_norm +
            self.pesos.custo * custo_ops_norm +
            self.pesos.emissao * custo_emissao_norm +
            self.pesos.rejeicao * custo_rejeicao_norm
        )