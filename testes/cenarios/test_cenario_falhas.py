"""
Testes de Cenários - Falha em estações
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido

class TestCenarioFalhas(unittest.TestCase):
    
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=True,
            prob_falha=0.2
        )
    
    def test_veiculos_lidam_com_falhas(self):
        """Veículos devem buscar estações alternativas."""
        # Força falha na estação central
        self.simulador.gestor_falhas.forcar_falha("Recarga_Centro", tempo_atual=0)
        
        # Cria pedidos que requerem recarga
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i * 5,
                prioridade=2,
                pref_ambiental="eletrico",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            self.simulador.agendar_pedido(pedido)
        
        # Reduz autonomia dos veículos elétricos
        for v in self.gestor.veiculos.values():
            if v.tipo_veiculo() == "eletrico":
                v.autonomia_km = 15.0  # Baixa autonomia
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        
        # Deve ter atendido pelo menos alguns (usando outras estações)
        self.assertGreater(metricas['pedidos_servicos'], 0)

if __name__ == '__main__':
    unittest.main()