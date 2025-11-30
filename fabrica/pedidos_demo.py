from modelo.pedidos import Pedido, EstadoPedido
from gestao.simulador import Simulador

"""Gera pedidos de transporte para testes de simulação."""
class PedidosDemo:

    @staticmethod
    def criar_pedidos_demo(simulador: Simulador):
        p1 = Pedido(
            id_pedido="P1",
            posicao_inicial="Shopping", 
            posicao_destino="Aeroporto",  
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
            posicao_inicial="Hospital",
            posicao_destino="Porto",
            passageiros=1,
            instante_pedido=3,
            prioridade=1,
            pref_ambiental="combustao",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None
        )

        p3 = Pedido(
            id_pedido="P3",
            posicao_inicial="Universidade",
            posicao_destino="Parque_Tec",
            passageiros=1,
            instante_pedido=5,
            prioridade=1,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            instante_atendimento=None
        )

        simulador.agendar_pedido(p1)
        simulador.agendar_pedido(p2)
        simulador.agendar_pedido(p3)

        return simulador
    
