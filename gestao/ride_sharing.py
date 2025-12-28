"""
Sistema de Ride-Sharing para otimizar ocupação de veículos.

- Agrupar pedidos compatíveis
- Maximizar ocupação dos veículos
- Minimizar desvios de rota
- Respeitar restrições de capacidade e tempo
"""

from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import math
from modelo.pedidos import Pedido
from modelo.veiculos import Veiculo
from modelo.grafo import Grafo
from gestao.algoritmos_procura.uteis import dist_euclidiana

@dataclass
class GrupoPedidos:
    """Grupo de pedidos compatíveis para ride-sharing."""
    pedidos: List[Pedido]
    origem_comum: str  # Zona de pickup compartilhada
    destino_comum: str  # Zona de drop-off compartilhada
    passageiros_total: int
    desvio_estimado_km: float  # Desvio adicional vs viagens individuais
    economia_estimada: float  # Economia de km sem passageiros
    
    def e_viavel(self, capacidade_veiculo: int) -> bool:
        """Verifica se grupo cabe no veículo."""
        return self.passageiros_total <= capacidade_veiculo
    
    def prioridade_minima(self) -> int:
        """Retorna prioridade mínima do grupo."""
        return min(p.prioridade for p in self.pedidos)


class GestorRideSharing:
    """
    Gestor de ride-sharing para agrupar pedidos compatíveis.
    
    CRITÉRIOS DE COMPATIBILIDADE:
    1. Proximidade geográfica (origem e destino)
    2. Janela temporal compatível
    3. Capacidade do veículo
    4. Desvio aceitável de rota
    """
    
    def __init__(self, grafo: Grafo, raio_agrupamento_km: float = 2.0, janela_temporal_min: int = 5, desvio_maximo_km: float = 3.0):

        self.grafo = grafo
        self.raio_agrupamento = raio_agrupamento_km
        self.janela_temporal = janela_temporal_min
        self.desvio_maximo = desvio_maximo_km
        
        # Estatísticas
        self.grupos_criados = 0
        self.pedidos_agrupados = 0
        self.economia_total_km = 0.0
    
    def distancia_euclidiana(self, no1_id: str, no2_id: str) -> float:
        """
        Wrapper que chama a função importada dist_euclidiana.
        Mantém compatibilidade com chamadas self.distancia_euclidiana().
        """
        no1 = self.grafo.nos[no1_id]
        no2 = self.grafo.nos[no2_id]
        return dist_euclidiana(no1, no2)
    
    def pedidos_compativel_temporal(self, p1: Pedido, p2: Pedido) -> bool:
        """Verifica se pedidos são compatíveis temporalmente."""
        diff = abs(p1.instante_pedido - p2.instante_pedido)
        return diff <= self.janela_temporal
    
    def pedidos_compativel_espacial(self, p1: Pedido, p2: Pedido) -> bool:
        """
        Verifica se pedidos são compatíveis espacialmente.
        Critério: Origens E destinos devem estar próximos.
        """
        dist_origem = self.distancia_euclidiana(p1.posicao_inicial, p2.posicao_inicial)
        dist_destino = self.distancia_euclidiana(p1.posicao_destino, p2.posicao_destino)
        
        return (dist_origem <= self.raio_agrupamento and 
                dist_destino <= self.raio_agrupamento)
    
    def encontrar_grupos_compativeis(self, pedidos: List[Pedido],
                                     capacidade_maxima: int = 4) -> List[GrupoPedidos]:
        """
        Encontra grupos de pedidos compatíveis para ride-sharing.
        1. Ordena pedidos por tempo
        2. Para cada pedido, procura compatíveis na janela temporal
        3. Agrupa pedidos que atendem critérios espaciais
        4. Valida capacidade do veículo
        
        Returns:
            Lista de grupos viáveis
        """
        if len(pedidos) < 2:
            return []
        
        # Ordena por tempo de pedido
        pedidos_ordenados = sorted(pedidos, key=lambda p: p.instante_pedido)
        
        grupos = []
        visitados: Set[str] = set()
        
        for i, p1 in enumerate(pedidos_ordenados):
            if p1.id_pedido in visitados:
                continue
            
            # Inicia novo grupo
            grupo_atual = [p1]
            passageiros = p1.passageiros
            visitados.add(p1.id_pedido)
            
            # procura pedidos compatíveis
            for p2 in pedidos_ordenados[i+1:]:
                if p2.id_pedido in visitados:
                    continue
                
                # Verifica compatibilidade
                if not self.pedidos_compativel_temporal(p1, p2):
                    break  # Fora da janela temporal
                
                if not self.pedidos_compativel_espacial(p1, p2):
                    continue  # Longe demais
                
                # Verifica capacidade
                if passageiros + p2.passageiros > capacidade_maxima:
                    continue  # Excede capacidade
                
                # Adiciona ao grupo
                grupo_atual.append(p2)
                passageiros += p2.passageiros
                visitados.add(p2.id_pedido)
            
            # Se agrupou 2+ pedidos, cria GrupoPedidos
            if len(grupo_atual) >= 2:
                grupo = self.criar_grupo(grupo_atual, passageiros)
                if grupo and grupo.desvio_estimado_km <= self.desvio_maximo:
                    grupos.append(grupo)
        
        return grupos
    
    def criar_grupo(self, pedidos: List[Pedido], passageiros_total: int) -> Optional[GrupoPedidos]:
        """
        Cria objeto GrupoPedidos com métricas calculadas.
        Escolhe origem/destino "central" do grupo.
        """
        # Origem: centróide das origens
        origem_central = self.encontrar_zona_central([p.posicao_inicial for p in pedidos])
        
        # Destino: centróide dos destinos
        destino_central = self.encontrar_zona_central([p.posicao_destino for p in pedidos])
        
        if not origem_central or not destino_central:
            return None
        
        # Calcula desvio estimado
        desvio = self.calcular_desvio_total(pedidos, origem_central, destino_central)
        
        # Calcula economia (km que seriam percorridos individualmente)
        economia = self.calcular_economia(pedidos, origem_central, destino_central)
        
        return GrupoPedidos(
            pedidos=pedidos,
            origem_comum=origem_central,
            destino_comum=destino_central,
            passageiros_total=passageiros_total,
            desvio_estimado_km=desvio,
            economia_estimada=economia
        )
    
    def encontrar_zona_central(self, zonas: List[str]) -> Optional[str]:
        """
        Encontra zona mais central de um conjunto - zona com menor distância total para todas as outras.
        """
        if not zonas:
            return None
        
        if len(zonas) == 1:
            return zonas[0]
        
        menor_dist_total = float('inf')
        zona_central = None
        
        for candidata in set(zonas):  # Remove duplicadas
            dist_total = sum(
                self.dist_euclidiana(candidata, z) 
                for z in zonas if z != candidata
            )
            
            if dist_total < menor_dist_total:
                menor_dist_total = dist_total
                zona_central = candidata
        
        return zona_central
    
    def calcular_desvio_total(self, pedidos: List[Pedido], origem_comum: str, destino_comum: str) -> float:
        """
        Calcula desvio adicional causado pelo agrupamento.
        Desvio = soma das distâncias extras de cada pedido até o ponto comum.
        """
        desvio_total = 0.0
        
        for pedido in pedidos:
            desvio_origem = self.dist_euclidiana(pedido.posicao_inicial, origem_comum)
            desvio_destino = self.dist_euclidiana(pedido.posicao_destino, destino_comum)
            
            desvio_total += desvio_origem + desvio_destino
        
        return desvio_total
    
    def calcular_economia(self, pedidos: List[Pedido], origem_comum: str, destino_comum: str) -> float:
        """
        Calcula economia de km sem passageiros (dead mileage).
        Economia = (km individuais) - (km agrupados)
        """
        # Distância se fossem viagens individuais
        # (assumindo veículos começam na mesma posição)
        km_individuais = len(pedidos) * self.dist_euclidiana(
            origem_comum, destino_comum
        )
        
        # Distância agrupada (uma única viagem)
        km_agrupados = self.dist_euclidiana(origem_comum, destino_comum)
        
        return km_individuais - km_agrupados
    
    def aplicar_ride_sharing(self, pedidos: List[Pedido], veiculo: Veiculo, gestor_frota) -> Optional[Tuple[List[Pedido], List[str]]]:
        """
        Aplica ride-sharing: agrupa pedidos compatíveis e calcula rota otimizada.

        Returns:
            (pedidos_agrupados, rota_otimizada) ou None se não viável
        """
        # Encontra grupos compatíveis
        grupos = self.encontrar_grupos_compativeis(
            pedidos, veiculo.capacidade_passageiros
        )
        
        if not grupos:
            return None
        
        # Seleciona melhor grupo (maior economia)
        melhor_grupo = max(grupos, key=lambda g: g.economia_estimada)
        
        # Valida capacidade
        if not melhor_grupo.e_viavel(veiculo.capacidade_passageiros):
            return None
        
        # Calcula rota otimizada
        rota = self.calcular_rota_otimizada(
            veiculo, melhor_grupo, gestor_frota
        )
        
        if not rota:
            return None
        
        # Atualiza estatísticas
        self.grupos_criados += 1
        self.pedidos_agrupados += len(melhor_grupo.pedidos)
        self.economia_total_km += melhor_grupo.economia_estimada
        
        return melhor_grupo.pedidos, rota
    
    def calcular_rota_otimizada(self, veiculo: Veiculo, grupo: GrupoPedidos, gestor_frota) -> Optional[List[str]]:
        """
        Calcula rota otimizada para atender grupo de pedidos.
        
        Estratégia:
        1. Posição atual → Origem comum (pickup de todos)
        2. Origem comum → Destino comum (viagem compartilhada)
        """
        # Rota até pickup
        viavel_pickup, rota_pickup, _, _ = gestor_frota.verificar_viabilidade_rota(veiculo, veiculo.posicao, grupo.origem_comum)
        if not viavel_pickup:
            return None
        
        # Rota da viagem partilhada
        viavel_viagem, rota_viagem, _, _ = gestor_frota.verificar_viabilidade_rota(veiculo, grupo.origem_comum, grupo.destino_comum)
        if not viavel_viagem:
            return None
        
        # Combina rotas
        rota_completa = rota_pickup + rota_viagem[1:]
        
        return rota_completa
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas do sistema de ride-sharing."""
        return {
            "grupos_criados": self.grupos_criados,
            "pedidos_agrupados": self.pedidos_agrupados,
            "economia_total_km": round(self.economia_total_km, 2),
            "economia_media_por_grupo": (
                round(self.economia_total_km / self.grupos_criados, 2)
                if self.grupos_criados > 0 else 0.0
            )
        }