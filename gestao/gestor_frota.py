from __future__ import annotations
from typing import Dict, List, Optional
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from modelo.grafo import Grafo, TipoNo
from gestao.metricas import Metricas
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs
from gestao.funcao_custo import FuncaoCustoComposta, PesosCusto

'''
    Classe responsável pela gestão da frota da TaxiGreen. 
    Mantém o estado dos veículos e pedidos, controla atribuições
'''
class GestorFrota:

    def __init__(self, grafo: Grafo, usar_funcao_custo_composta: bool = False):
        self.grafo = grafo
        self.veiculos: Dict[str, Veiculo] = {}
        self.pedidos_pendentes: List[Pedido] = []
        self.pedidos_concluidos: List[Pedido] = []
        self.metricas = Metricas()
        self.algoritmo_procura = "astar"

        self.usar_funcao_custo_composta = usar_funcao_custo_composta
        self.funcao_custo = FuncaoCustoComposta()


    # ==========================================================
    # Gestão de algoritmos de procura
    # ==========================================================

    def definir_algoritmo_procura(self, nome: str):
        """Escolhe qual algoritmo de procura usar: astar, ucs, bfs ou dfs"""
        if nome.lower() in ("astar", "ucs", "bfs", "dfs"):
            self.algoritmo_procura = nome.lower()
        else:
            raise ValueError("Algoritmo desconhecido. Use: astar, ucs, bfs ou dfs.")
    

    def calcular_rota(self, origem: str, destino: str, veiculo=None):
        """
        Calcula rota considerando veículo (se fornecido) para heurística avançada

        Args:
            origem: Nó de origem
            destino: Nó de destino
            veiculo: (Opcional) Veículo para heurística avançada

        Returns:
            (caminho, custo)
        """
        if origem == destino:
            return [origem], 0.0

        if origem not in self.grafo.nos or destino not in self.grafo.nos:
            print(f"Erro: Nó inexistente - origem:{origem}, destino:{destino}")
            return [], float('inf')

        try:
            if self.algoritmo_procura == "astar":
                # Passa veículo para heurística avançada
                custo, caminho = a_star_search(
                    self.grafo, origem, destino, 
                    veiculo=veiculo, 
                    tempo_atual=getattr(self, 'tempo_atual', 0),
                    usar_heuristica_avancada=True  # Pode ser configurável
                )
            elif self.algoritmo_procura == "ucs":
                custo, caminho = uniform_cost_search(self.grafo, origem, destino)
            elif self.algoritmo_procura == "bfs":
                caminho = bfs(self.grafo, origem, destino)
                custo = self.calcular_custo_rota(caminho) if caminho else float('inf')
            elif self.algoritmo_procura == "dfs":
                caminho = dfs(self.grafo, origem, destino)
                custo = self.calcular_custo_rota(caminho) if caminho else float('inf')
            else:
                raise ValueError("Algoritmo não definido")

            if not caminho or custo == float('inf'):
                print(f"Nenhum caminho encontrado: {origem} → {destino}")
                return [], float('inf')

            return caminho, custo

        except Exception as e:
            print(f"Erro ao calcular rota {origem}→{destino}: {e}")
            return [], float('inf')



    def calcular_custo_rota(self, caminho: List[str]) -> float:
        if not caminho or len(caminho) < 2:
            return 0.0

        custo_total = 0.0
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                custo_total += aresta.tempo_real()  # Considera trânsito
            except ValueError:
                return float('inf')  # Caminho inválido

        return custo_total


    def calcular_distancia_rota(self, caminho: List[str]) -> float:
        if not caminho or len(caminho) < 2:
            return 0.0
        
        distancia = 0.0
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                distancia += aresta.distancia_km
            except ValueError:
                return float('inf')
        
        return distancia
    

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

    """
    Move veículo para zona de alta procura esperada
    """
    def reposicionar_veiculo(veiculo, pedidos_futuros):

        # Analisa pedidos futuros (próximos 10 minutos)
        zonas_procura = {}
        for p in pedidos_futuros:
            if p.instante_pedido <= tempo_atual + 10:
                zona = p.posicao_inicial
                zonas_procura[zona] = zonas_procura.get(zona, 0) + 1

        # Move para zona de maior procura
        if zonas_procura:
            zona_alvo = max(zonas_procura, key=zonas_procura.get)
            veiculo.definir_rota(calcular_rota(veiculo.posicao, zona_alvo))

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


    def selecionar_veiculo_pedido(self, pedido: Pedido, tempo_atual: int) -> Optional[Veiculo]:
        """
        Seleciona veículo considerando custo composto (se ativado)
        """
        candidatos = [
            v for v in self.veiculos_disponiveis(tempo_atual)
            if v.pode_transportar(pedido.passageiros)
        ]
    
        if not candidatos:
            return None
    
        # Filtra por preferência ambiental
        if pedido.pref_ambiental in ("eletrico", "combustao"):
            preferidos = [v for v in candidatos
                         if v.tipo_veiculo() == pedido.pref_ambiental]
            if preferidos:
                candidatos = preferidos
    
        melhor_veiculo = None
        
        if self.usar_custo_composto:
            # Usa função de custo composta
            menor_custo_composto = float('inf')
            
            for v in candidatos:
                caminho, custo_tempo = self.calcular_rota(v.posicao, pedido.posicao_inicial, veiculo=v)
                distancia = self.calcular_distancia_rota(caminho)
                
                if distancia == float('inf') or not v.consegue_percorrer(distancia):
                    continue
                
                # Calcula tempo de resposta
                tempo_resposta = tempo_atual - pedido.instante_pedido + custo_tempo
                
                # Calcula distância total (pickup + viagem)
                rota_viagem, _ = self.calcular_rota(pedido.posicao_inicial, pedido.posicao_destino, veiculo=v)
                dist_viagem = self.calcular_distancia_rota(rota_viagem)
                dist_total = distancia + dist_viagem
                
                # Calcula custo composto
                custo_composto = self.funcao_custo.calcular_custo_atribuicao(
                    v, pedido, tempo_resposta, dist_total
                )
                
                if custo_composto < menor_custo_composto:
                    menor_custo_composto = custo_composto
                    melhor_veiculo = v
        
        else:
            # Usa apenas tempo/distância
            menor_custo = float('inf')
            
            for v in candidatos:
                caminho, custo = self.calcular_rota(v.posicao, pedido.posicao_inicial, veiculo=v)
                distancia = self.calcular_distancia_rota(caminho)
                
                if distancia == float('inf') or not v.consegue_percorrer(distancia):
                    continue
                
                if custo < menor_custo:
                    menor_custo = custo
                    melhor_veiculo = v
    
        return melhor_veiculo

    def atribuir_pedido(self, pedido: Pedido, tempo_atual: int) -> Optional[Veiculo]:
        v_escolhido = self.selecionar_veiculo_pedido(pedido, tempo_atual)
        if not v_escolhido:
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
       
        rota_ate_origem, custo_origem = self.calcular_rota(v_escolhido.posicao, pedido.posicao_inicial )
        rota_para_destino, custo_destino = self.calcular_rota(pedido.posicao_inicial, pedido.posicao_destino)
        
        if not rota_ate_origem or not rota_para_destino:
            print(f"Pedido {pedido.id_pedido} rejeitado: sem rota viável")
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None

        # Verifica autonomia total necessária
        dist_total = (self.calcular_distancia_rota(rota_ate_origem) + self.calcular_distancia_rota(rota_para_destino))
        
        if not v_escolhido.consegue_percorrer(dist_total):
            # Tenta incluir recarga no meio
            return self.atribuir_com_recarga(pedido, v_escolhido, tempo_atual)
        
        rota_completa = rota_ate_origem + rota_para_destino[1:]
        
        # Remove nós consecutivos duplicados (segurança extra)
        rota_filtrada = [rota_completa[0]]
        for no in rota_completa[1:]:
            if no != rota_filtrada[-1]:
                rota_filtrada.append(no)
        
        # Atribui veículo
        pedido.veiculo_atribuido = v_escolhido.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        pedido.instante_atendimento = tempo_atual
        
        v_escolhido.definir_rota(rota_filtrada)
        v_escolhido.estado = EstadoVeiculo.EM_DESLOCACAO
        v_escolhido.id_pedido_atual = pedido.id_pedido
        
        return v_escolhido


    # Tenta atribuir pedido incluindo paragem para recarga
    def atribuir_com_recarga(self, pedido: Pedido, veiculo: Veiculo, tempo_atual: int) -> Optional[Veiculo]:

        # Encontra estação de recarga mais próxima (que esteja disponível)
        estacoes = [no_id for no_id, no in self.grafo.nos.items()
                    if veiculo.pode_carregar_abastecer(no.tipo) and no.disponivel]
        
        if not estacoes:
            print(f"ERRO: Sem estações de {veiculo.tipo_veiculo()} disponíveis")
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
        
        melhor_estacao = None
        melhor_rota = None
        menor_custo = float('inf')
        
        for estacao in estacoes:
            # Rota: posição atual → estação → origem pedido → destino pedido
            rota1, c1 = self.calcular_rota(veiculo.posicao, estacao)
            rota2, c2 = self.calcular_rota(estacao, pedido.posicao_inicial)
            rota3, c3 = self.calcular_rota(pedido.posicao_inicial, pedido.posicao_destino)
            
            if not all([rota1, rota2, rota3]):
                continue
            
            custo_total = c1 + c2 + c3
            if custo_total < menor_custo:
                menor_custo = custo_total
                melhor_estacao = estacao
                melhor_rota = rota1 + rota2[1:] + rota3[1:]
        
        if not melhor_rota:
            pedido.estado = EstadoPedido.REJEITADO
            self.metricas.pedidos_rejeitados += 1
            return None
        
        # Atribui com rota incluindo recarga
        pedido.veiculo_atribuido = veiculo.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        pedido.instante_atendimento = tempo_atual
        
        veiculo.definir_rota(melhor_rota)
        veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        veiculo.id_pedido_atual = pedido.id_pedido
        
        print(f"Veículo {veiculo.id_veiculo} vai recarregar em {melhor_estacao}")
        return veiculo


    def verificar_necessidade_recarga(self, veiculo: Veiculo, tempo_atual: int, threshold: float = 0.3) -> bool:

        if veiculo.estado != EstadoVeiculo.DISPONIVEL:
            return False

        if veiculo.autonomia_km > (threshold * veiculo.autonomiaMax_km):
            return False

        # Encontra estação mais próxima (que esteja disponível)
        estacoes = [no_id for no_id, no in self.grafo.nos.items()
                   if veiculo.pode_carregar_abastecer(no.tipo) and no.disponivel]
        
        if not estacoes:
            return False
        
        # Calcula rota para estação mais próxima
        melhor_estacao = None
        melhor_rota = None
        menor_dist = float('inf')
        
        for estacao in estacoes:
            rota, custo = self.calcular_rota(veiculo.posicao, estacao)
            dist = self.calcular_distancia_rota(rota)
            
            if dist < menor_dist and veiculo.consegue_percorrer(dist):
                menor_dist = dist
                melhor_estacao = estacao
                melhor_rota = rota
        
        if not melhor_rota:
            print(f"Veículo {veiculo.id_veiculo} sem autonomia para chegar a estação!")
            veiculo.estado = EstadoVeiculo.INDISPONIVEL
            return False
        
        # Define rota para estação
        veiculo.definir_rota(melhor_rota)
        veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        print(f"Veículo {veiculo.id_veiculo} vai recarregar em {melhor_estacao}")
        
        return True
    
    # Agrupa pedidos que estão geograficamente próximos
    def agrupar_pedidos_proximos(pedidos_pendentes, raio_km=5.0):
        clusters = []
        visitados = set()

        for p1 in pedidos_pendentes:
            if p1.id_pedido in visitados:
                continue

            cluster = [p1]
            visitados.add(p1.id_pedido)

            for p2 in pedidos_pendentes:
                if p2.id_pedido in visitados:
                    continue

                # Verifica proximidade de origem E destino
                dist_origem = self.grafo.distancia(p1.posicao_inicial, p2.posicao_inicial)
                dist_destino = self.grafo.distancia(p1.posicao_destino, p2.posicao_destino)

                if dist_origem <= raio_km and dist_destino <= raio_km:
                    cluster.append(p2)
                    visitados.add(p2.id_pedido)

            clusters.append(cluster)

        return clusters