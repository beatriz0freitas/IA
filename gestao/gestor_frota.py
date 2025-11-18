"""
GestorFrota COMPLETO com Ride-Sharing integrado
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from modelo.grafo import Grafo, TipoNo
from gestao.metricas import Metricas
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs


class GestorFrota:
    """
    Classe responsável pela gestão da frota da TaxiGreen.
    Suporta atribuição individual e ride-sharing de pedidos.
    """

    def __init__(self, grafo: Grafo, usar_ride_sharing: bool = True):
        self.grafo = grafo
        self.veiculos: Dict[str, Veiculo] = {}
        self.pedidos_pendentes: List[Pedido] = []
        self.pedidos_concluidos: List[Pedido] = []
        self.metricas = Metricas()
        self.algoritmo_procura = "astar"
        self.usar_ride_sharing = usar_ride_sharing
        
        # Importar ride-sharing apenas se necessário
        if usar_ride_sharing:
            from gestao.ride_sharing import RideSharing
            self.ride_sharing = RideSharing(self)
        else:
            self.ride_sharing = None

    # ========== GESTÃO DE ALGORITMOS DE PROCURA ==========

    def definir_algoritmo_procura(self, nome: str):
        """Escolhe qual algoritmo de procura usar"""
        if nome.lower() not in ("astar", "ucs", "bfs", "dfs"):
            raise ValueError(
                "Algoritmo desconhecido. Use: astar, ucs, bfs ou dfs."
            )
        self.algoritmo_procura = nome.lower()

    def calcular_rota(self, origem: str, destino: str) -> Tuple[List[str], float]:
        """
        Calcula rota entre dois nós usando o algoritmo definido.
        Retorna: (caminho, custo_tempo_minutos)
        """
        if origem == destino:
            return [origem], 0.0

        try:
            if self.algoritmo_procura == "astar":
                custo, caminho = a_star_search(self.grafo, origem, destino)
            elif self.algoritmo_procura == "ucs":
                custo, caminho = uniform_cost_search(self.grafo, origem, destino)
            elif self.algoritmo_procura == "bfs":
                caminho = bfs(self.grafo, origem, destino)
                custo = self._calcular_tempo_rota(caminho)
            elif self.algoritmo_procura == "dfs":
                caminho = dfs(self.grafo, origem, destino)
                custo = self._calcular_tempo_rota(caminho)
            else:
                raise ValueError("Algoritmo não definido")

            return caminho, custo
        except (ValueError, KeyError) as e:
            print(f"⚠ Erro ao calcular rota {origem}→{destino}: {e}")
            return [], float('inf')

    def _calcular_tempo_rota(self, caminho: List[str]) -> float:
        """Soma o tempo de viagem das arestas ao longo do caminho"""
        if not caminho or len(caminho) < 2:
            return 0.0

        tempo = 0.0
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                tempo += aresta.tempoViagem_min
            except ValueError:
                return float('inf')
        return tempo

    # ========== GESTÃO DE VEÍCULOS ==========

    def adicionar_veiculo(self, v: Veiculo):
        """Adiciona veículo à frota"""
        self.veiculos[v.id_veiculo] = v

    def veiculos_disponiveis(self) -> List[Veiculo]:
        """Retorna lista de veículos DISPONIVEL"""
        return [
            v for v in self.veiculos.values()
            if v.estado == EstadoVeiculo.DISPONIVEL
        ]

    def get_veiculo(self, id_veiculo: str) -> Optional[Veiculo]:
        """Obtém veículo por ID"""
        return self.veiculos.get(id_veiculo)

    # ========== GESTÃO DE PEDIDOS ==========

    def adicionar_pedido(self, p: Pedido):
        """Adiciona pedido à lista de pendentes"""
        self.pedidos_pendentes.append(p)

    def pedidos_ativos(self) -> List[Pedido]:
        """Retorna pedidos PENDENTE ou ATRIBUIDO"""
        return [
            p for p in self.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO)
        ]

    # ========== SELEÇÃO E ATRIBUIÇÃO DE VEÍCULOS ==========

    def selecionar_veiculo_pedido(self, pedido: Pedido) -> Optional[Veiculo]:
        """
        Seleciona o melhor veículo para um pedido.
        Critério: veículo com capacidade suficiente e menor distância à origem.
        """
        candidatos = []

        for v in self.veiculos_disponiveis():
            # Verificar capacidade
            if not v.pode_transportar(pedido.passageiros):
                continue

            # Verificar preferência ambiental
            if pedido.pref_ambiental != "qualquer":
                if v.tipo_veiculo() != pedido.pref_ambiental:
                    continue

            # Verificar autonomia
            try:
                dist_ate_origem = self.grafo.distancia(v.posicao, pedido.posicao_inicial)
                if not v.consegue_percorrer(dist_ate_origem):
                    continue
            except ValueError:
                continue

            candidatos.append(v)

        if not candidatos:
            return None

        def distancia_total(v):
            try:
                return self.grafo.distancia(v.posicao, pedido.posicao_inicial)
            except ValueError:
                return float("inf")

        return min(candidatos, key=distancia_total)

    def atribuir_pedido(self, pedido: Pedido) -> Optional[Veiculo]:
        """
        Atribui um pedido a um veículo e calcula a rota completa.
        Com ride-sharing: agrega múltiplos pedidos no mesmo veículo.
        """
        print(f"\n🎯 ATRIBUINDO PEDIDO {pedido.id_pedido}")

        # Se ride-sharing ativo
        if self.usar_ride_sharing and self.ride_sharing:
            # Adicionar pedido aos pendentes
            if pedido not in self.pedidos_pendentes:
                self.pedidos_pendentes.append(pedido)

            # Tentar agrupar e atribuir
            grupos_atribuidos = self.ride_sharing.atribuir_grupos_otimizado()

            if grupos_atribuidos:
                # Retornar veículo do grupo contendo este pedido
                for grupo in grupos_atribuidos:
                    if pedido in grupo.pedidos:
                        print(f"   ✓ Pedido {pedido.id_pedido} agrupado com outros passageiros")
                        return grupo.veiculo

        # Atribuição individual (sem ride-sharing ou ride-sharing falhou)
        return self._atribuir_individual(pedido)

    def _atribuir_individual(self, pedido: Pedido) -> Optional[Veiculo]:
        """Atribuição individual de um pedido"""
        v_escolhido = self.selecionar_veiculo_pedido(pedido)
        if not v_escolhido:
            pedido.estado = EstadoPedido.REJEITADO
            print(f"   ❌ Nenhum veículo disponível para {pedido.id_pedido}")
            return None

        print(f"   Veículo escolhido: {v_escolhido.id_veiculo}")
        print(f"   Posição atual: {v_escolhido.posicao}")

        # Marcar pedido como atribuído
        pedido.veiculo_atribuido = v_escolhido.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        v_escolhido.estado = EstadoVeiculo.EM_DESLOCACAO

        # Calcular rota: posição_atual → origem → destino
        print(f"   Calculando rota 1: {v_escolhido.posicao} → {pedido.posicao_inicial}")
        rota1, tempo1 = self.calcular_rota(
            v_escolhido.posicao, pedido.posicao_inicial
        )
        print(f"   Rota 1: {rota1} (tempo: {tempo1:.1f} min)")

        print(f"   Calculando rota 2: {pedido.posicao_inicial} → {pedido.posicao_destino}")
        rota2, tempo2 = self.calcular_rota(
            pedido.posicao_inicial, pedido.posicao_destino
        )
        print(f"   Rota 2: {rota2} (tempo: {tempo2:.1f} min)")

        if not rota1 or not rota2:
            pedido.estado = EstadoPedido.REJEITADO
            v_escolhido.estado = EstadoVeiculo.DISPONIVEL
            print(f"   ❌ Não conseguiu calcular rota completa")
            return None

        # Juntar rotas
        rota_completa = rota1 + rota2[1:]
        print(f"   Rota antes de filtrar: {rota_completa}")

        # Remover nós repetidos consecutivos
        rota_filtrada = []
        for no in rota_completa:
            if not rota_filtrada or no != rota_filtrada[-1]:
                rota_filtrada.append(no)

        print(f"   Rota depois de filtrar: {rota_filtrada}")
        print(f"   Rota final: {rota_filtrada}")
        v_escolhido.definir_rota(rota_filtrada)
        print(f"   ✓ Pedido {pedido.id_pedido} atribuído a {v_escolhido.id_veiculo}")
        return v_escolhido

    # ========== MÉTODOS AUXILIARES ==========

    def gerar_estado_atual(self) -> Dict:
        """Gera representação do estado atual do sistema"""
        return {
            "tempo_simulacao": 0,
            "veiculos": {
                v.id_veiculo: {
                    "posicao": v.posicao,
                    "estado": v.estado.value,
                    "autonomia": v.autonomia_km,
                    "tipo": v.tipo_veiculo()
                }
                for v in self.veiculos.values()
            },
            "pedidos_pendentes": [p.id_pedido for p in self.pedidos_pendentes],
            "pedidos_concluidos": [p.id_pedido for p in self.pedidos_concluidos],
        }