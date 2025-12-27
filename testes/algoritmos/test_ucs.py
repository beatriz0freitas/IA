"""
Testes de Algoritmos de Procura - UCS
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.algoritmos_procura.ucs import uniform_cost_search

class TestUCS(unittest.TestCase):
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_caminho_minimo(self):
        """Testa que UCS encontra caminho de custo mínimo."""
        from gestao.algoritmos_procura.ucs import uniform_cost_search
        
        custo, caminho = uniform_cost_search(
            self.grafo, "Centro", "Hospital"
        )
        
        self.assertTrue(caminho)
        self.assertGreater(custo, 0.0)
    
    def test_consistencia(self):
        """Testa que UCS sempre retorna mesmo resultado."""
        from gestao.algoritmos_procura.ucs import uniform_cost_search
        
        custo1, caminho1 = uniform_cost_search(self.grafo, "Centro", "Porto")
        custo2, caminho2 = uniform_cost_search(self.grafo, "Centro", "Porto")
        
        self.assertEqual(custo1, custo2)
        self.assertEqual(caminho1, caminho2)

if __name__ == '__main__':
    unittest.main()