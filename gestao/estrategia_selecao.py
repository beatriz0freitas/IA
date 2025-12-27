"""
Padrão Strategy para seleção de veículos.
Permite trocar critérios de seleção facilmente sem modificar GestorFrota.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from modelo.pedidos import Pedido
from modelo.veiculos import Veiculo

if TYPE_CHECKING:
    from gestao.gestor_frota import GestorFrota

class EstrategiaSelecao(ABC):
    """Interface base para estratégias de seleção de veículos."""
    
    @abstractmethod
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        """
        Seleciona melhor veículo para atender pedido.
    
        Returns:
            Veículo selecionado ou None se nenhum adequado
        """
        pass


class SelecaoMenorDistancia(EstrategiaSelecao):
    """
    Estratégia simples: seleciona veículo mais próximo.
    Critério: menor tempo até origem do pedido.
    """
    
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        
        melhor_veiculo = None
        menor_custo = float('inf')
        
        for veiculo in candidatos:
            # Verifica viabilidade
            viavel, caminho, custo, distancia = gestor.verificar_viabilidade_rota(
                veiculo, veiculo.posicao, pedido.posicao_inicial
            )
            
            if not viavel:
                continue
            
            # Verifica autonomia para viagem completa
            _, caminho_viagem, _, dist_viagem = gestor.verificar_viabilidade_rota(
                veiculo, pedido.posicao_inicial, pedido.posicao_destino
            )
            
            if not veiculo.consegue_percorrer(distancia + dist_viagem):
                continue
            
            if custo < menor_custo:
                menor_custo = custo
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class SelecaoCustoComposto(EstrategiaSelecao):
    """
    Estratégia avançada: considera múltiplos objetivos.
    Usa função de custo composta (tempo, custo operacional, emissões).
    """
    
    def __init__(self, funcao_custo):
        self.funcao_custo = funcao_custo
    
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        
        melhor_veiculo = None
        menor_custo_composto = float('inf')
        
        for veiculo in candidatos:
            # Rota até pickup
            viavel_pickup, caminho_pickup, custo_pickup, dist_pickup = \
                gestor.verificar_viabilidade_rota(
                    veiculo, veiculo.posicao, pedido.posicao_inicial
                )
            
            if not viavel_pickup:
                continue
            
            # Rota da viagem
            viavel_viagem, caminho_viagem, custo_viagem, dist_viagem = \
                gestor.verificar_viabilidade_rota(
                    veiculo, pedido.posicao_inicial, pedido.posicao_destino
                )
            
            if not viavel_viagem:
                continue
            
            # Verifica autonomia total
            distancia_total = dist_pickup + dist_viagem
            if not veiculo.consegue_percorrer(distancia_total):
                continue
            
            # Calcula tempo de resposta
            tempo_resposta = tempo_atual - pedido.instante_pedido + custo_pickup
            
            # Calcula custo composto
            custo_composto = self.funcao_custo.calcular_custo_atribuicao(
                veiculo, pedido, tempo_resposta, distancia_total
            )
            
            if custo_composto < menor_custo_composto:
                menor_custo_composto = custo_composto
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class SelecaoDeadMileage(EstrategiaSelecao):
    """
    Estratégia focada em minimizar km sem passageiros.
    Penaliza veículos distantes do pedido.
    """
    
    def __init__(self, penalizacao: float = 2.0):
        """
        Args:
            penalizacao: Fator de penalização para dead mileage (default: 2x)
        """
        self.penalizacao = penalizacao
    
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        
        melhor_veiculo = None
        menor_custo_ponderado = float('inf')
        
        for veiculo in candidatos:
            # Distância até pickup (DEAD MILEAGE)
            viavel_pickup, _, custo_pickup, dist_pickup = \
                gestor.verificar_viabilidade_rota(
                    veiculo, veiculo.posicao, pedido.posicao_inicial
                )
            
            if not viavel_pickup:
                continue
            
            # Distância da viagem (ÚTIL)
            viavel_viagem, _, custo_viagem, dist_viagem = \
                gestor.verificar_viabilidade_rota(
                    veiculo, pedido.posicao_inicial, pedido.posicao_destino
                )
            
            if not viavel_viagem:
                continue
            
            # Verifica autonomia
            if not veiculo.consegue_percorrer(dist_pickup + dist_viagem):
                continue
            
            # Custo ponderado: PENALIZA dead mileage
            custo_dead = dist_pickup * self.penalizacao  # 2x penalização
            custo_util = dist_viagem * 1.0               # Normal
            custo_ponderado = custo_dead + custo_util
            
            if custo_ponderado < menor_custo_ponderado:
                menor_custo_ponderado = custo_ponderado
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class SelecaoEquilibrada(EstrategiaSelecao):
    """
    Estratégia híbrida: equilibra distância, custo e sustentabilidade.
    Boa opção padrão para uso geral.
    """
    
    def __init__(self, peso_distancia: float = 0.5, peso_custo: float = 0.3, peso_emissao: float = 0.2):
        self.peso_distancia = peso_distancia
        self.peso_custo = peso_custo
        self.peso_emissao = peso_emissao
    
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        
        melhor_veiculo = None
        menor_score = float('inf')
        
        # Normalização
        MAX_DIST = 50.0  # km
        MAX_CUSTO = 50.0  # €
        MAX_EMISSAO = 5.0  # kg CO2
        
        for veiculo in candidatos:
            viavel, caminho, custo_tempo, distancia = \
                gestor.verificar_viabilidade_rota(
                    veiculo, veiculo.posicao, pedido.posicao_inicial
                )
            
            if not viavel:
                continue
            
            # Viagem completa
            _, _, _, dist_viagem = gestor.verificar_viabilidade_rota(
                veiculo, pedido.posicao_inicial, pedido.posicao_destino
            )
            
            dist_total = distancia + dist_viagem
            if not veiculo.consegue_percorrer(dist_total):
                continue
            
            # Métricas normalizadas
            score_distancia = (distancia / MAX_DIST)
            score_custo = (veiculo.custo_operacao(dist_total) / MAX_CUSTO)
            score_emissao = (veiculo.calcula_emissao(dist_total) / MAX_EMISSAO)
            
            # Score ponderado
            score = (
                self.peso_distancia * score_distancia +
                self.peso_custo * score_custo +
                self.peso_emissao * score_emissao
            )
            
            if score < menor_score:
                menor_score = score
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class SelecaoPriorizarEletricos(EstrategiaSelecao):
    """
    Estratégia sustentável: prioriza veículos elétricos.
    Só escolhe combustão se nenhum elétrico disponível.
    """
    
    def __init__(self, estrategia_base: EstrategiaSelecao = None):
        """
        Args:
            estrategia_base: Estratégia a usar após filtrar por tipo
        """
        self.estrategia_base = estrategia_base or SelecaoMenorDistancia()
    
    def selecionar(self, pedido: Pedido, candidatos: List[Veiculo], gestor: 'GestorFrota', tempo_atual: int) -> Optional[Veiculo]:
        
        # Filtra elétricos
        eletricos = [v for v in candidatos if v.tipo_veiculo() == "eletrico"]
        
        # Tenta primeiro com elétricos
        if eletricos:
            veiculo = self.estrategia_base.selecionar(
                pedido, eletricos, gestor, tempo_atual
            )
            if veiculo:
                return veiculo
        
        # Fallback: aceita combustão
        combustao = [v for v in candidatos if v.tipo_veiculo() == "combustao"]
        if combustao:
            return self.estrategia_base.selecionar(
                pedido, combustao, gestor, tempo_atual
            )
        
        return None