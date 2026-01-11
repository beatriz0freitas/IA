"""
Testes de Cenários - Pedidos Urgentes vs Normais
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes

class TestCenarioPrioridadeUrgente(unittest.TestCase):
 
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_prioridade_alta_atendida_primeiro(self):
        """Pedidos urgentes devem ser atendidos primeiro."""
        # Pedido urgente
        pedido_urgente = Pedido(
            id_pedido="P_URGENTE",
            posicao_inicial="Centro",
            posicao_destino="Hospital",
            passageiros=1,
            instante_pedido=5,
            prioridade=3,  # Máxima
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            tempo_max_espera=10
        )
        
        # Pedidos normais
        pedidos_normais = []
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P_NORMAL{i}",
                posicao_inicial="Shopping",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=4,  # Chegaram antes!
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            pedidos_normais.append(pedido)
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.agendar_pedido(pedido_urgente)
        
        # Instante 4 - chegam normais
        self.simulador.tempo_atual = 4
        self.simulador.processar_pedidos_novos()

        # Instante 5 - chega urgente
        self.simulador.tempo_atual = 5
        self.simulador.processar_pedidos_novos()

        # Instante 7 - aguarda 2 minutos para atribuir (pedido mais antigo em t=4)
        self.simulador.tempo_atual = 7
        self.simulador.atribuir_pedidos_pendentes()

        # Pedido urgente deve ser atendido
        self.assertIsNotNone(pedido_urgente.veiculo_atribuido)

if __name__ == '__main__':
    unittest.main()