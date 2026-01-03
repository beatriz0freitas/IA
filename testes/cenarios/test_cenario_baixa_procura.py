"""
Testes de Cenários - Baixa Procura
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes

class TestCenarioBaixaDemanda(unittest.TestCase):
    
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_todos_pedidos_atendidos(self):
        """Com baixa procura, todos devem ser atendidos."""
        # 3 pedidos espaçados
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 10,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=60  # Tempo generoso
            )
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        self.assertEqual(metricas['pedidos_servicos'], 3)
        self.assertEqual(metricas['pedidos_rejeitados'], 0)
        self.assertEqual(metricas['taxa_sucesso'], 100.0)


if __name__ == '__main__':
    unittest.main()