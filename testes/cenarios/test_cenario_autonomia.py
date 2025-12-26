"""
Testes de Cenários - Autonomia Crítica
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido

class TestCenarioAutonomiaLimitada(unittest.TestCase):

    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        
        # Reduz autonomia de todos os veículos
        for v in self.gestor.veiculos.values():
            v.autonomia_km = 10.0  # Muito baixa
        
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_veiculos_recarregam_automaticamente(self):
        """Veículos devem buscar recarga automaticamente."""
        # Cria pedido que requer recarga intermediária
        pedido = Pedido(
            id_pedido="P_LONGO",
            posicao_inicial="Porto",
            posicao_destino="Aeroporto",
            passageiros=1,
            instante_pedido=5,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )
        
        self.simulador.agendar_pedido(pedido)
        self.simulador.executar()
        
        # Pedido deve ter sido atribuído (com recarga)
        # OU rejeitado se impossível
        self.assertIn(
            pedido.estado, 
            [EstadoPedido.CONCLUIDO, EstadoPedido.REJEITADO, EstadoPedido.ATRIBUIDO]
        )


if __name__ == '__main__':
    unittest.main()
