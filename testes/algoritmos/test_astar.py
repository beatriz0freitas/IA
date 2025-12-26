"""
Testes de Algoritmos de Procura - A*
"""

import unittest
from gestao.algoritmos_procura.a_estrela import a_star_search
from testes.test_config import ConfigTestes


class TestAStar(unittest.TestCase):
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_caminho_direto(self):
        """Testa caminho simples."""
        custo, caminho = a_star_search(self.grafo, "Centro", "Shopping")
        
        self.assertTrue(caminho)
        self.assertEqual(caminho[0], "Centro")
        self.assertEqual(caminho[-1], "Shopping")
        self.assertLess(custo, float('inf'))
    
    def test_origem_igual_destino(self):
        """Testa que origem=destino retorna custo zero."""
        custo, caminho = a_star_search(self.grafo, "Centro", "Centro")
        
        self.assertEqual(custo, 0.0)
        self.assertEqual(caminho, ["Centro"])
    
    def test_otimalidade(self):
        """Testa que A* encontra solução ótima."""
        from gestao.algoritmos_procura.ucs import uniform_cost_search
        
        custo_astar, _ = a_star_search(self.grafo, "Porto", "Aeroporto")
        custo_ucs, _ = uniform_cost_search(self.grafo, "Porto", "Aeroporto")
        
        # A* deve ter custo igual ou melhor (com heurística admissível)
        self.assertAlmostEqual(custo_astar, custo_ucs, places=2)
    
    def test_caminho_longo(self):
        """Testa caminho através da cidade."""
        custo, caminho = a_star_search(
            self.grafo, "Suburbio_Oeste1", "Aeroporto"
        )
        
        self.assertTrue(caminho)
        self.assertGreater(len(caminho), 3)

if __name__ == '__main__':
    unittest.main()