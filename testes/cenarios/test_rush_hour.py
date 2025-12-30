"""
Teste de cenário: Rush Hour com trânsito intenso.
"""

import unittest
from gestao.simulador import Simulador
from gestao.transito_dinamico import GestorTransito
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestCenarioRushHour(unittest.TestCase):
    
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=True,
            usar_falhas=False
        )
    
    def test_transito_aumenta_tempos(self):
        """Verifica que trânsito aumenta tempos de viagem."""
        grafo = self.simulador.gestor.grafo
        
        # Salva tempo base
        aresta_ref = grafo.get_aresta("Centro", "Shopping")
        tempo_base = aresta_ref.tempo_minutos
        
        # Madrugada (2h)
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=120)
        aresta_noite = grafo.get_aresta("Centro", "Shopping")
        tempo_noturno = aresta_noite.tempo_real()
        
        # Rush hour (8h)
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)
        aresta_rush = grafo.get_aresta("Centro", "Shopping")
        tempo_rush = aresta_rush.tempo_real()
        
        # Verificações corretas
        self.assertLess(tempo_noturno, tempo_base * 1.1)
        self.assertGreater(tempo_rush, tempo_base * 1.5)
        self.assertGreater(tempo_rush, tempo_noturno)
    
    def test_pedidos_atendidos_com_transito(self):
        """Testa que pedidos são atendidos mesmo com trânsito."""
        for i in range(5):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 2, 
                prioridade=2,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=None
            )
            self.simulador.agendar_pedido(pedido)
        
        # Aplica congestionamento
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        self.assertGreater(metricas['pedidos_servicos'], 0)


if __name__ == '__main__':
    unittest.main()