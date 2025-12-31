"""
Testes de Cenários - Alta Procura (Stress Test)
"""

import unittest
from gestao.simulador import Simulador
from testes.test_config import ConfigTestes
from modelo.pedidos import Pedido, EstadoPedido

class TestCenarioAltaDemanda(unittest.TestCase):

    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=40,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_capacidade_limitada(self):
        """Com alta procura, alguns podem ser rejeitados."""
        # 15 pedidos simultâneos
        for i in range(15):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=2,
                instante_pedido=5,  # Todos no mesmo instante
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=20
            )
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        total = metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']
        
        self.assertGreaterEqual(total, 14, "Deve processar pelo menos 14 dos 15 pedidos")
        # Com 4 veículos, não deve conseguir atender todos simultaneamente
        self.assertGreater(metricas['pedidos_rejeitados'], 0)

if __name__ == '__main__':
    unittest.main()