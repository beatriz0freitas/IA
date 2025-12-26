"""
Testes de Algoritmos de Procura - DFS
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.algoritmos_procura.dfs import dfs

class TestDFS(unittest.TestCase):
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_encontra_algum_caminho(self):
        """Testa que DFS encontra caminho (não necessariamente ótimo)."""
        from gestao.algoritmos_procura.dfs import dfs
        
        caminho = dfs(self.grafo, "Centro", "Hospital")
        
        self.assertTrue(caminho)
        self.assertEqual(caminho[0], "Centro")
        self.assertEqual(caminho[-1], "Hospital")
    
    def test_dfs_vs_bfs(self):
        """Compara tamanhos de caminhos DFS vs BFS."""
        from gestao.algoritmos_procura.dfs import dfs
        from gestao.algoritmos_procura.bfs import bfs
        
        caminho_dfs = dfs(self.grafo, "Porto", "Escola_Norte")
        caminho_bfs = bfs(self.grafo, "Porto", "Escola_Norte")
        
        # BFS tende a encontrar caminhos mais curtos
        if caminho_dfs and caminho_bfs:
            self.assertGreaterEqual(len(caminho_dfs), len(caminho_bfs))

if __name__ == '__main__':
    unittest.main()