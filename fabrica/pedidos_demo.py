from modelo.pedidos import Pedido, EstadoPedido
from gestao.simulador import Simulador

"""Gera pedidos de transporte para testes de simulação."""
class PedidosDemo:

    @staticmethod
    def criar_pedidos_demo(simulador: Simulador):
        p1 = Pedido(
            id_pedido="P1",
            posicao_inicial="A",
            posicao_destino="B",
            passageiros=2,
            instante_pedido=0,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None
        )

        p2 = Pedido(
            id_pedido="P2",
            posicao_inicial="C",
            posicao_destino="D",
            passageiros=1,
            instante_pedido=3,
            prioridade=1,
            pref_ambiental="combustao",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None
        )

        simulador.agendar_pedido(p1)
        simulador.agendar_pedido(p2)

        return simulador
    
