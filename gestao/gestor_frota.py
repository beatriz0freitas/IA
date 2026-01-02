"""
    Classe responsável pela gestão da frota da TaxiGreen. 

Responsabilidades:
- Gestão de veículos e pedidos
- Cálculo de rotas (delega aos algoritmos)
- Atribuição de veículos (delega às estratégias)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from modelo.grafo import Grafo, TipoNo
from gestao.metricas import Metricas
from gestao.cache_distancias import CacheDistancias, CacheRotas
from gestao.estrategia_selecao import (EstrategiaSelecao, SelecaoMenorDistancia, SelecaoCustoComposto)
from gestao.reposicionamento import reposicionar_veiculo_proativo

from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs
from gestao.algoritmos_procura.greedy import greedy


class GestorFrota:

    def __init__(self, grafo: Grafo, estrategia_selecao: EstrategiaSelecao = None):
        self.grafo = grafo
        self.veiculos: Dict[str, Veiculo] = {}
        self.pedidos_pendentes: List[Pedido] = []
        self.pedidos_concluidos: List[Pedido] = []
        self.metricas = Metricas()
        self.algoritmo_procura = "astar"
        
        self.cache_distancias = CacheDistancias(grafo)
        self.cache_rotas = CacheRotas(validade_minutos=10)
        
        # Estratégia de seleção (padrão: menor distância)
        self.estrategia_selecao = estrategia_selecao or SelecaoMenorDistancia()
        
        # Pré-carrega distâncias entre estações
        self.pre_carregar_cache()

    def pre_carregar_cache(self):
        """Pré-carrega cache com distâncias entre estações/postos."""
        estacoes = [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo in (TipoNo.ESTACAO_RECARGA, TipoNo.POSTO_ABASTECIMENTO)
        ]
        self.cache_distancias.pre_carregar_distancias_criticas(estacoes)


    # ==========================================================
    # Gestão de algoritmos de procura
    # ==========================================================

    def definir_algoritmo_procura(self, nome: str):
        """Escolhe qual algoritmo de procura usar: astar, ucs, bfs ou dfs"""
        if nome.lower() in ("astar", "greedy", "ucs", "bfs", "dfs"):
            self.algoritmo_procura = nome.lower()
        else:
            raise ValueError("Algoritmo desconhecido. Use: astar, greedy, ucs, bfs ou dfs.")
    
    def definir_estrategia_selecao(self, estrategia: EstrategiaSelecao):
        """Troca estratégia de seleção de veículos."""
        self.estrategia_selecao = estrategia

    # ==========================================================
    # CÁLCULO DE ROTAS (OTIMIZADO)
    # ==========================================================

    def calcular_rota(self, origem: str, destino: str, 
                     veiculo: Veiculo = None, tempo_atual: int = 0) -> Tuple[List[str], float]:
        """
        Calcula rota entre dois nós (com cache).
            -tempo_atual: Tempo atual (para trânsito)
            
        Returns:
            (caminho, custo_tempo)
        """
        if origem == destino:
            return [origem], 0.0
        
        if origem not in self.grafo.nos or destino not in self.grafo.nos:
            return [], float('inf')
        
        # Tenta buscar no cache
        resultado_cache = self.cache_rotas.get_rota(
            origem, destino, self.algoritmo_procura, tempo_atual
        )
        if resultado_cache:
            return resultado_cache
        
        # Cache miss - calcula rota
        try:
            if self.algoritmo_procura == "astar":
                custo, caminho = a_star_search(self.grafo, origem, destino, veiculo=veiculo, tempo_atual=tempo_atual, usar_heuristica_avancada=True)
            elif self.algoritmo_procura == "ucs":
                custo, caminho = uniform_cost_search(self.grafo, origem, destino)
            elif self.algoritmo_procura == "bfs":
                caminho = bfs(self.grafo, origem, destino)
                custo = self.calcular_custo_caminho(caminho) if caminho else float('inf')
            elif self.algoritmo_procura == "dfs":
                caminho = dfs(self.grafo, origem, destino)
                custo = self.calcular_custo_caminho(caminho) if caminho else float('inf')
            elif self.algoritmo_procura == "greedy":
                custo, caminho = greedy(self.grafo, origem, destino)
            else:
                return [], float('inf')
            
            if caminho and custo != float('inf'):
                # Armazena no cache
                self.cache_rotas.armazenar_rota(
                    origem, destino, self.algoritmo_procura, 
                    caminho, custo, tempo_atual
                )
                return caminho, custo
            
            return [], float('inf')
        
        except Exception as e:
            print(f"Erro ao calcular rota {origem}→{destino}: {e}")
            return [], float('inf')


    def calcular_metricas_rota(self, caminho: List[str]) -> Tuple[float, float]:
        """
        Calcula custo (tempo) E distância de uma rota simultaneamente.
        
        Returns:
            (custo_tempo, distancia_km)
        """
        if not caminho or len(caminho) < 2:
            return 0.0, 0.0
        
        custo_total = 0.0
        distancia_total = 0.0
        
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                custo_total += aresta.tempo_real()
                distancia_total += aresta.distancia_km
            except ValueError:
                return float('inf'), float('inf')
        
        return custo_total, distancia_total
    
    def calcular_custo_caminho(self, caminho: List[str]) -> float:
        """Calcula apenas custo (para BFS/DFS)."""
        custo, _ = self.calcular_metricas_rota(caminho)
        return custo
    
    def verificar_viabilidade_rota(self, veiculo: Veiculo, origem: str, destino: str) -> Tuple[bool, List[str], float, float]:
        """
        Verifica se veículo pode completar rota.
        
        Returns:
            (viavel, caminho, custo_tempo, distancia)
        """
        caminho, custo = self.calcular_rota(origem, destino, veiculo=veiculo)
        
        if not caminho or custo == float('inf'):
            return False, [], float('inf'), float('inf')
        
        _, distancia = self.calcular_metricas_rota(caminho)
        viavel = veiculo.consegue_percorrer(distancia)
        
        return viavel, caminho, custo, distancia
    

    # ==========================================================
    # Gestão de veículos
    # ==========================================================
    def adicionar_veiculo(self, v: Veiculo):
        if v.posicao not in self.grafo.nos:
            raise ValueError(f"Posição inicial '{v.posicao}' não existe no grafo")
        if v.autonomia_km <= 0 or v.autonomiaMax_km <= 0:
            raise ValueError(f"Veículo {v.id_veiculo}: autonomia deve ser > 0")
        
        self.veiculos[v.id_veiculo] = v

    def veiculos_disponiveis(self, tempo_atual: int = 0) -> List[Veiculo]:
        return [
            v for v in self.veiculos.values()
            if v.estado == EstadoVeiculo.DISPONIVEL 
            and tempo_atual >= v.tempo_ocupado_ate
        ]

    def get_veiculo(self, id_veiculo: str) -> Optional[Veiculo]:
        return self.veiculos.get(id_veiculo)
    


    def reposicionar_veiculos(self, tempo_atual: int, pedidos_futuros: List):
        """
        Reposiciona veículos ociosos para zonas de alta demanda.
        """
        from gestao.reposicionamento import reposicionar_veiculo_proativo

        veiculos_ociosos = [v for v in self.veiculos.values()
                           if v.estado == EstadoVeiculo.DISPONIVEL and not v.rota]

        if not veiculos_ociosos:
            return

        reposicionamentos = []
        for veiculo in veiculos_ociosos:
            zona_alvo = reposicionar_veiculo_proativo(
                veiculo, pedidos_futuros, tempo_atual, self.grafo, janela_previsao=10
            )

            # Se zona alvo é diferente da posição atual
            if zona_alvo != veiculo.posicao:
                reposicionamentos.append((veiculo.id_veiculo, veiculo.posicao, zona_alvo))

                # Calcula rota para zona alvo
                viavel, rota, _, _ = self.verificar_viabilidade_rota(veiculo, veiculo.posicao, zona_alvo)
                if viavel and len(rota) > 1:
                    veiculo.rota = rota
                    veiculo.indice_rota = 0

        return reposicionamentos


    # ==========================================================
    # Gestão de pedidos
    # ==========================================================
    def adicionar_pedido(self, p: Pedido):
        if p.posicao_inicial not in self.grafo.nos:
            raise ValueError(f"Pedido {p.id_pedido}: origem '{p.posicao_inicial}' inválida")
        if p.posicao_destino not in self.grafo.nos:
            raise ValueError(f"Pedido {p.id_pedido}: destino '{p.posicao_destino}' inválido")
        if p.passageiros <= 0:
            raise ValueError(f"Pedido {p.id_pedido}: número de passageiros inválido")
        
        self.pedidos_pendentes.append(p)

    def filtrar_veiculos_por_preferencia(self, candidatos: List[Veiculo], pref_ambiental: str) -> List[Veiculo]:
        """
        Filtra veículos por preferência ambiental.
        """
        if pref_ambiental in ("eletrico", "combustao"):
            preferidos = [v for v in candidatos 
                         if v.tipo_veiculo() == pref_ambiental]
            return preferidos if preferidos else candidatos
        return candidatos
    
    def selecionar_veiculo_pedido(self, pedido: Pedido, tempo_atual: int) -> Optional[Veiculo]:
        """
        Seleciona veículo para pedido usando estratégia configurada.
        """
        # Filtra candidatos básicos
        candidatos = [
            v for v in self.veiculos_disponiveis(tempo_atual)
            if v.pode_transportar(pedido.passageiros)
        ]
        
        if not candidatos:
            return None
        
        # Aplica filtro de preferência ambiental
        candidatos = self.filtrar_veiculos_por_preferencia(candidatos, pedido.pref_ambiental)
        
        return self.estrategia_selecao.selecionar(pedido, candidatos, self, tempo_atual)


    def atribuir_pedido(self, pedido: Pedido, tempo_atual: int) -> Optional[Veiculo]:
        """Atribui veículo a pedido."""
        veiculo = self.selecionar_veiculo_pedido(pedido, tempo_atual)
        
        if not veiculo:
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
        
        # Calcula rota completa (pickup + viagem)
        viavel_pickup, rota_pickup, _, _ = self.verificar_viabilidade_rota(veiculo, veiculo.posicao, pedido.posicao_inicial)
        viavel_viagem, rota_viagem, _, _ = self.verificar_viabilidade_rota(veiculo, pedido.posicao_inicial, pedido.posicao_destino)
        
        if not viavel_pickup or not viavel_viagem:
            return self.atribuir_com_recarga(pedido, veiculo, tempo_atual)
        
        # Monta rota completa
        rota_completa = rota_pickup + rota_viagem[1:]
        
        # Remove duplicados consecutivos (segurança)
        rota_filtrada = [rota_completa[0]]
        for no in rota_completa[1:]:
            if no != rota_filtrada[-1]:
                rota_filtrada.append(no)
        
        # Atribui
        pedido.veiculo_atribuido = veiculo.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        pedido.instante_atendimento = tempo_atual
        
        veiculo.definir_rota(rota_filtrada)
        veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        veiculo.id_pedido_atual = pedido.id_pedido
        
        return veiculo


    # Tenta atribuir pedido incluindo paragem para recarga
    def atribuir_com_recarga(self, pedido: Pedido, veiculo: Veiculo, tempo_atual: int) -> Optional[Veiculo]:

        # Encontra estação de recarga mais próxima (que esteja disponível)
        estacoes = [
            no_id for no_id, no in self.grafo.nos.items()
            if veiculo.pode_carregar_abastecer(no.tipo) and no.disponivel]
        
        if not estacoes:
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
        
        melhor_estacao = None
        melhor_rota = None
        menor_custo = float('inf')
        
        for estacao in estacoes:
            # Rota: posição atual → estação → origem pedido → destino pedido
            viavel1, r1, c1, _ = self.verificar_viabilidade_rota(veiculo, veiculo.posicao, estacao)
            viavel2, r2, c2, _ = self.verificar_viabilidade_rota(veiculo, estacao, pedido.posicao_inicial)
            viavel3, r3, c3, _ = self.verificar_viabilidade_rota(veiculo, pedido.posicao_inicial, pedido.posicao_destino )
            
            if not all([viavel1, viavel2, viavel3]):
                continue
            
            custo_total = c1 + c2 + c3
            if custo_total < menor_custo:
                menor_custo = custo_total
                melhor_estacao = estacao
                melhor_rota = r1 + r2[1:] + r3[1:]
        
        if not melhor_rota:
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
        
        # Atribui com recarga
        pedido.veiculo_atribuido = veiculo.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        pedido.instante_atendimento = tempo_atual
        
        veiculo.definir_rota(melhor_rota)
        veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        veiculo.id_pedido_atual = pedido.id_pedido
        
        return veiculo


    def verificar_necessidade_recarga(self, veiculo: Veiculo, tempo_atual: int, threshold: float = 0.3) -> bool:
        """Verifica se veículo precisa recarregar e envia para estação."""

        if veiculo.estado != EstadoVeiculo.DISPONIVEL:
            return False

        if veiculo.autonomia_km > (threshold * veiculo.autonomiaMax_km):
            return False

        # Encontra estação mais próxima (que esteja disponível)
        estacoes = [
            no_id for no_id, no in self.grafo.nos.items()
            if veiculo.pode_carregar_abastecer(no.tipo) and no.disponivel]
        
        if not estacoes:
            return False
        
        # Calcula rota para estação mais próxima
        melhor_estacao = None
        melhor_rota = None
        menor_dist = float('inf')
        
        for estacao in estacoes:
            viavel, rota, _, dist = self.verificar_viabilidade_rota(veiculo, veiculo.posicao, estacao)
            
            if viavel and dist < menor_dist:
                menor_dist = dist
                melhor_estacao = estacao
                melhor_rota = rota
        
        if not melhor_rota:
            veiculo.estado = EstadoVeiculo.INDISPONIVEL
            return False
        
        veiculo.definir_rota(melhor_rota)
        veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        return True

    # ==========================================================
    # ESTATÍSTICAS
    # ==========================================================
    
    def obter_estatisticas_cache(self) -> dict:
        """Retorna estatísticas dos caches."""
        return {
            "cache_distancias": self.cache_distancias.estatisticas(),
            "cache_rotas": self.cache_rotas.estatisticas()
        }
    