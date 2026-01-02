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
        aresta = grafo.get_aresta("Centro", "Shopping")
        
        # 1. Madrugada (02:00) - deve ter menos trânsito
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=120)
        congestion_madrugada = aresta.congestion
        tempo_madrugada = aresta.tempo_real()
        
        # 2. Rush hour manhã (08:00) - deve ter muito mais trânsito
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)
        congestion_rush = aresta.congestion
        tempo_rush = aresta.tempo_real()
        
        # 3. Tarde normal (14:00) - trânsito moderado
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=840)
        congestion_tarde = aresta.congestion
                
        # Madrugada tem menos trânsito que rush
        self.assertLess(congestion_madrugada, congestion_rush,
                       f"Madrugada ({congestion_madrugada:.2f}) deve ter menos que Rush ({congestion_rush:.2f})")
        
        # Rush tem tempo maior que madrugada
        self.assertGreater(tempo_rush, tempo_madrugada,
                          f"Tempo Rush ({tempo_rush:.2f}) > Madrugada ({tempo_madrugada:.2f})")
        
        # Rush é o período com MAIS trânsito
        self.assertGreater(congestion_rush, congestion_tarde,
                          f"Rush ({congestion_rush:.2f}) deve ter mais que Tarde ({congestion_tarde:.2f})")
    
    def test_factor_hora_correto(self):
        """Testa que factors de hora estão corretos."""
        gestor_transito = self.simulador.gestor_transito
        
        # Valores esperados (do método calcular_factor_hora)
        self.assertEqual(gestor_transito.calcular_factor_hora(2), 0.8)   # Madrugada
        self.assertEqual(gestor_transito.calcular_factor_hora(8), 1.8)   # Rush manhã
        self.assertEqual(gestor_transito.calcular_factor_hora(12), 1.3)  # Almoço
        self.assertEqual(gestor_transito.calcular_factor_hora(18), 2.0)  # Rush tarde
        self.assertEqual(gestor_transito.calcular_factor_hora(15), 1.0)  # Normal
        
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