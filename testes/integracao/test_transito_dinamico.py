
"""
Testes de Integração - Transito Dinâmico
"""

import unittest
from testes.test_config import ConfigTestes

class TestTransitoDinamico(unittest.TestCase):
    
    def setUp(self):
        from gestao.transito_dinamico import GestorTransito
        
        self.grafo = ConfigTestes.criar_grafo_teste()
        self.gestor_transito = GestorTransito(self.grafo)
    
    def test_factor_hora_rush_manha(self):
        """Testa fator durante rush da manhã."""
        factor = self.gestor_transito.calcular_factor_hora(8)
        self.assertGreater(factor, 1.0)
    
    def test_factor_hora_noite(self):
        """Testa fator durante noite."""
        factor = self.gestor_transito.calcular_factor_hora(2)
        self.assertLess(factor, 1.0)
    
    def test_atualizar_transito_modifica_arestas(self):
        """Testa que atualização modifica congestionamento."""
        aresta = self.grafo.get_aresta("Centro", "Shopping")
        congestion_inicial = aresta.congestion
        
        # Atualiza para rush hour
        self.gestor_transito.atualizar_transito(tempo_simulacao=480)  # 8h
        
        congestion_rush = aresta.congestion
        
        # Congestionamento deve aumentar em zonas centrais
        self.assertGreaterEqual(congestion_rush, congestion_inicial)
    
    def test_bloqueio_estrada(self):
        """Testa bloqueio de estrada."""
        sucesso = self.gestor_transito.simular_bloqueio(
            "Centro", "Shopping", bloquear=True
        )
        
        self.assertTrue(sucesso)
        
        aresta = self.grafo.get_aresta("Centro", "Shopping")
        self.assertTrue(aresta.blocked)
        self.assertEqual(aresta.tempo_real(), float('inf'))
    
    def test_desbloqueio(self):
        """Testa desbloqueio de estrada."""
        self.gestor_transito.simular_bloqueio("Centro", "Shopping", bloquear=True)
        self.gestor_transito.simular_bloqueio("Centro", "Shopping", bloquear=False)
        
        aresta = self.grafo.get_aresta("Centro", "Shopping")
        self.assertFalse(aresta.blocked)
    
    def test_estado_transito(self):
        """Testa obtenção de estado do trânsito."""
        estado = self.gestor_transito.obter_estado_transito()
        
        self.assertIn("hora_atual", estado)
        self.assertIn("congestion_media", estado)
        self.assertGreater(estado['total_estradas'], 0)

if __name__ == '__main__':
    unittest.main()