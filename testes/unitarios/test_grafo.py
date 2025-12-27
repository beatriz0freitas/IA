"""
Testes Unitários - Grafo
"""

import unittest
from modelo.grafo import Grafo, No, Aresta, TipoNo
from testes.test_config import ConfigTestes


class TestGrafo(unittest.TestCase):
    
    def setUp(self):
        """Cria grafo simples para testes."""
        self.grafo = Grafo()
        
        # Adiciona nós
        self.grafo.adiciona_no(No("A", 0, 0, TipoNo.RECOLHA_PASSAGEIROS))
        self.grafo.adiciona_no(No("B", 1, 0, TipoNo.RECOLHA_PASSAGEIROS))
        self.grafo.adiciona_no(No("C", 1, 1, TipoNo.ESTACAO_RECARGA))
        
        # Adiciona arestas
        self.grafo.adiciona_aresta("A", "B", 1.0, 2.0)
        self.grafo.adiciona_aresta("B", "C", 1.4, 3.0)
    
    def test_adicionar_no(self):
        """Testa adição de nós."""
        self.assertIn("A", self.grafo.nos)
        self.assertIn("B", self.grafo.nos)
        self.assertEqual(len(self.grafo.nos), 3)
    
    def test_adicionar_aresta_bidirecional(self):
        """Testa que arestas são bidirecionais."""
        # A → B existe
        aresta_ab = self.grafo.get_aresta("A", "B")
        self.assertEqual(aresta_ab.no_destino, "B")
        
        # B → A também existe
        aresta_ba = self.grafo.get_aresta("B", "A")
        self.assertEqual(aresta_ba.no_destino, "A")
        
        # Mesma distância
        self.assertEqual(aresta_ab.distancia_km, aresta_ba.distancia_km)
    
    def test_vizinhos(self):
        """Testa obtenção de vizinhos."""
        vizinhos_a = self.grafo.vizinhos("A")
        self.assertEqual(len(vizinhos_a), 1)
        self.assertEqual(vizinhos_a[0].no_destino, "B")
    
    def test_aresta_inexistente(self):
        """Testa exceção para aresta inexistente."""
        with self.assertRaises(ValueError):
            self.grafo.get_aresta("A", "C")
    
    def test_distancia(self):
        """Testa cálculo de distância entre nós."""
        dist = self.grafo.distancia("A", "B")
        self.assertEqual(dist, 1.0)
    
    def test_congestionamento_inicial(self):
        """Testa que congestionamento inicial é 1.0."""
        aresta = self.grafo.get_aresta("A", "B")
        self.assertEqual(aresta.congestion, 1.0)
        self.assertEqual(aresta.tempo_real(), 2.0)
    
    def test_bloqueio_aresta(self):
        """Testa bloqueio de aresta."""
        aresta = self.grafo.get_aresta("A", "B")
        aresta.blocked = True
        
        self.assertEqual(aresta.tempo_real(), float('inf'))

if __name__ == '__main__':
    unittest.main()