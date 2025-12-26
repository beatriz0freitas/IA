from modelo.pedidos import Pedido, EstadoPedido
from gestao.simulador import Simulador

"""Gera pedidos de transporte para testes de simulação."""
class PedidosDemo:

    @staticmethod
    def criar_pedidos_demo(simulador: Simulador):
        # Pedido 1: Cliente no Shopping quer ir ao Hospital
        p1 = Pedido(
            id_pedido="P1",
            posicao_inicial="Shopping",
            posicao_destino="Hospital",
            passageiros=2,
            instante_pedido=1,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None,
            tempo_max_espera=15
        )

        # Pedido 2: Cliente no Centro quer ir ao Aeroporto
        p2 = Pedido(
            id_pedido="P2",
            posicao_inicial="Centro",
            posicao_destino="Aeroporto",
            passageiros=1,
            instante_pedido=2,
            prioridade=3,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None,
            tempo_max_espera=20
        )

        # Pedido 3: Cliente na Universidade quer ir à Praia
        p3 = Pedido(
            id_pedido="P3",
            posicao_inicial="Universidade",
            posicao_destino="Praia",
            passageiros=3,
            instante_pedido=3,
            prioridade=1,
            pref_ambiental="combustao",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None,
            tempo_max_espera=25
        )

        # Pedido 4: Cliente no Porto quer ir ao Estadio
        p4 = Pedido(
            id_pedido="P4",
            posicao_inicial="Porto",
            posicao_destino="Estadio",
            passageiros=2,
            instante_pedido=5,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None,
            tempo_max_espera=30
        )

        # Pedido 5: Cliente no Parque_Tec quer ir ao Centro
        p5 = Pedido(
            id_pedido="P5",
            posicao_inicial="Parque_Tec",
            posicao_destino="Centro",
            passageiros=1,
            instante_pedido=7,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None,
            tempo_max_espera=20
        )

        simulador.agendar_pedido(p1)
        simulador.agendar_pedido(p2)
        simulador.agendar_pedido(p3)
        simulador.agendar_pedido(p4)
        simulador.agendar_pedido(p5)

        return simulador
    
