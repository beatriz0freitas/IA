"""
Testes de Algoritmos de Procura - BFS
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.algoritmos_procura.bfs import bfs_com_checkpoint

class TestBFS(unittest.TestCase):
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_encontra_caminho(self):
        """Testa que BFS encontra algum caminho."""
        from gestao.algoritmos_procura.bfs import bfs
        
        caminho = bfs(self.grafo, "Centro", "Shopping")
        
        self.assertTrue(caminho)
        self.assertIn("Centro", caminho)
        self.assertIn("Shopping", caminho)
    
    def test_caminho_inexistente(self):
        """Testa comportamento quando não há caminho."""
        from gestao.algoritmos_procura.bfs import bfs
        from modelo.grafo import Grafo, No, TipoNo
        
        # Cria grafo desconectado
        grafo_desc = Grafo()
        grafo_desc.adiciona_no(No("A", 0, 0, TipoNo.RECOLHA_PASSAGEIROS))
        grafo_desc.adiciona_no(No("B", 1, 1, TipoNo.RECOLHA_PASSAGEIROS))
        
        caminho = bfs(grafo_desc, "A", "B")
        self.assertEqual(caminho, [])
    
    def test_bfs_com_checkpoint(self):
        """Testa BFS com parada obrigatória."""
        from gestao.algoritmos_procura.bfs import bfs_com_checkpoint
        
        caminho = bfs_com_checkpoint(
            self.grafo, "Centro", "Shopping", "Aeroporto"
        )
        
        if caminho:  # Se existe caminho
            self.assertIn("Shopping", caminho)
            self.assertTrue(
                caminho.index("Centro") < caminho.index("Shopping") < caminho.index("Aeroporto")
            )

if __name__ == '__main__':
    unittest.main()