from __future__ import annotations
from typing import Dict, List, Optional
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from modelo.grafo import Grafo, TipoNo
from gestao.metricas import Metricas

'''
    Classe responsável pela gestão da frota da TaxiGreen. 
    Mantém o estado dos veículos e pedidos, controla atribuições
'''
class GestorFrota:

    def __init__(self, grafo: Grafo):
        self.grafo = grafo
        self.veiculos: Dict[str, Veiculo] = {}
        self.pedidos_pendentes: List[Pedido] = []
        self.pedidos_concluidos: List[Pedido] = []
        self.metricas = Metricas()


    # ==========================================================
    # Gestão de veículos
    # ==========================================================
    def adicionar_veiculo(self, v: Veiculo):
        self.veiculos[v.id_veiculo] = v

    def veiculos_disponiveis(self) -> List[Veiculo]:
        return [
            v for v in self.veiculos.values()
            if v.estado == EstadoVeiculo.DISPONIVEL
        ]

    def get_veiculo(self, id_veiculo: str) -> Optional[Veiculo]:
        return self.veiculos.get(id_veiculo)

    def tentar_recarregar(self, v: Veiculo) -> bool:
        tipo_no = self.grafo.nos[v.posicao].tipo
        return v.repor_autonomia(tipo_no)


    # ==========================================================
    # Gestão de pedidos
    # ==========================================================
    def adicionar_pedido(self, p: Pedido):
        self.pedidos_pendentes.append(p)

    def pedidos_ativos(self) -> List[Pedido]:
        return [
            p for p in self.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO)
        ]



    # Critério: veículo disponível com capacidade suficiente e menor distância até à origem do pedido.
    def selecionar_veiculo_pedido(self, pedido: Pedido) -> Optional[Veiculo]:
        candidatos = [
            v for v in self.veiculos_disponiveis()
            if v.pode_transportar(pedido.passageiros)
            and (v.tipo_veiculo() == pedido.pref_ambiental or pedido.pref_ambiental == "qualquer")
        ]

        if not candidatos:
            return None

        def distancia_total(v):
            try:
                return self.grafo.distancia(v.posicao, pedido.posicao_inicial)
            except ValueError:
                # caso a ligação não exista diretamente
                return float("inf")

        return min(candidatos, key=distancia_total)


    def atribuir_pedido(self, pedido: Pedido) -> Optional[Veiculo]:
        v_escolhido = self.selecionar_veiculo_pedido(pedido)
        if not v_escolhido:
            pedido.estado = EstadoPedido.REJEITADO
            return None
       
        pedido.veiculo_atribuido = v_escolhido.id_veiculo
        pedido.estado = EstadoPedido.ATRIBUIDO
        v_escolhido.estado = EstadoVeiculo.A_SERVICO

        # todo: adaptar para diferente selecao de algoritmo
        # nova rota = posição atual → recolha → destino
        rota = [v_escolhido.posicao, pedido.posicao_inicial, pedido.posicao_destino]

        #remove rós repetidos consecutivos
        rota_filtrada = [rota[0]]
        for no in rota[1:]:
            if no != rota_filtrada[-1]:
                rota_filtrada.append(no)

        v_escolhido.definir_rota(rota_filtrada)
        return v_escolhido




    # Execução de viagens e atualizações - custos, emissões, posição e autonomia.
    def executar_viagem(self, veiculo: Veiculo, pedido: Pedido, tempo_atual: int):
        # 1. Deslocar até à origem da viagem
        dist_origem = self.grafo.distancia(veiculo.posicao, pedido.posicao_inicial)
        if not veiculo.consegue_percorrer(dist_origem):
            pedido.estado = EstadoPedido.REJEITADO
            veiculo.estado = EstadoVeiculo.DISPONIVEL
            self.metricas.registar_pedido(pedido, tempo_resposta=tempo_atual - pedido.instante_pedido)
            return

        veiculo.move(dist_origem, pedido.posicao_inicial)
        self.metricas.integracao_metricas(veiculo, dist_origem)

        # 2. Levar passageiros até destino
        dist_viagem = self.grafo.distancia(pedido.posicao_inicial, pedido.posicao_destino)
        if not veiculo.consegue_percorrer(dist_viagem):
            pedido.estado = EstadoPedido.REJEITADO
            veiculo.estado = EstadoVeiculo.DISPONIVEL
            self.metricas.registar_pedido(pedido, tempo_resposta=tempo_atual - pedido.instante_pedido)
            return

        veiculo.move(dist_viagem, pedido.posicao_destino)
        self.metricas.integracao_metricas(veiculo, dist_viagem)

        pedido.estado = EstadoPedido.CONCLUIDO
        veiculo.estado = EstadoVeiculo.DISPONIVEL
        if pedido in self.pedidos_pendentes:
            self.pedidos_pendentes.remove(pedido)
        self.pedidos_concluidos.append(pedido)
        self.metricas.registar_pedido(pedido, tempo_resposta=tempo_atual - pedido.instante_pedido)









    # ==========================================================
    # 7️⃣ Integração futura com procura
    # ==========================================================
    def gerar_estado_atual(self) -> Dict:
        """
        Gera uma representação do estado atual do sistema
        (para algoritmos de procura).
        """
        return {
            "veiculos": {v.id_veiculo: v.posicao for v in self.veiculos.values()},
            "autonomias": {v.id_veiculo: v.autonomia_km for v in self.veiculos.values()},
            "pedidos_pendentes": [p.id_pedido for p in self.pedidos_pendentes],
        }
