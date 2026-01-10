"""
Teste Básico do Sistema de Trânsito
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.transito_dinamico import GestorTransito


class TestTransitoBasico(unittest.TestCase):
    """Testes básicos do sistema de trânsito."""
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
        # IMPORTANTE: hora_inicial = 0 (meia-noite)
        self.gestor = GestorTransito(self.grafo, hora_inicial=0)
    
    def test_hora_inicial_zero(self):
        """Testa que hora inicial é meia-noite."""
        self.assertEqual(self.gestor.hora_inicial, 0)
        self.assertEqual(self.gestor.hora_atual, 0)
    
    def test_calculo_hora(self):
        """Testa cálculo de hora atual."""
        # 120 minutos = 2 horas
        self.gestor.atualizar_hora(120)
        self.assertEqual(self.gestor.hora_atual, 2)
        
        # 480 minutos = 8 horas
        self.gestor.atualizar_hora(480)
        self.assertEqual(self.gestor.hora_atual, 8)
        
        # 1080 minutos = 18 horas
        self.gestor.atualizar_hora(1080)
        self.assertEqual(self.gestor.hora_atual, 18)
    
    def test_factors_hora(self):
        """Testa factors de cada período."""
        self.assertEqual(self.gestor.calcular_factor_hora(2), 0.8)   # Madrugada
        self.assertEqual(self.gestor.calcular_factor_hora(8), 1.8)   # Rush manhã
        self.assertEqual(self.gestor.calcular_factor_hora(12), 1.3)  # Almoço
        self.assertEqual(self.gestor.calcular_factor_hora(15), 1.0)  # Normal
        self.assertEqual(self.gestor.calcular_factor_hora(18), 2.0)  # Rush tarde
        self.assertEqual(self.gestor.calcular_factor_hora(22), 0.8)  # Noite
    
    def test_congestion_aplicado_corretamente(self):
        """Testa que congestionamento é aplicado às arestas."""
        aresta = self.grafo.get_aresta("Centro", "Shopping")
        
        # Madrugada - congestion deve ser 0.8 (ou próximo com multiplicador zona central)
        self.gestor.atualizar_transito(tempo_simulacao=120)
        cong1 = aresta.congestion
        self.assertLess(cong1, 1.5, f"Madrugada: {cong1}")
        
        # Rush - congestion deve ser > 1.5
        self.gestor.atualizar_transito(tempo_simulacao=480)
        cong2 = aresta.congestion
        self.assertGreater(cong2, 1.5, f"Rush: {cong2}")
        
        # Rush tarde - ainda maior
        self.gestor.atualizar_transito(tempo_simulacao=1080)
        cong3 = aresta.congestion
        self.assertGreater(cong3, cong2, f"Rush tarde ({cong3}) > Rush manhã ({cong2})")
    
    def test_tempo_real_aumenta_com_congestion(self):
        """Testa que tempo real reflete congestionamento."""
        aresta = self.grafo.get_aresta("Centro", "Shopping")
        tempo_base = aresta.tempoViagem_min
        
        # Madrugada
        self.gestor.atualizar_transito(tempo_simulacao=120)
        tempo1 = aresta.tempo_real()
        
        # Rush
        self.gestor.atualizar_transito(tempo_simulacao=480)
        tempo2 = aresta.tempo_real()
        
        # Tempo durante rush deve ser maior
        self.assertGreater(tempo2, tempo1, 
                          f"Rush ({tempo2:.2f}) deve ser > Madrugada ({tempo1:.2f})")


if __name__ == '__main__':
    unittest.main()