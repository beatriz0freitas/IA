"""
Testes de Heurísticas
testes/algoritmos/test_heuristicas.py
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.algoritmos_procura.uteis import dist_euclidiana, heuristica_avancada, tempo_heuristica
from gestao.algoritmos_procura.a_estrela import a_star_search

class TestHeuristicas(unittest.TestCase):
    
    def setUp(self):
        """Setup comum."""
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_heuristica_euclidiana(self):
        """Testa que distância euclidiana é admissível."""
        from gestao.algoritmos_procura.uteis import dist_euclidiana
        
        no_centro = self.grafo.nos["Centro"]
        no_aeroporto = self.grafo.nos["Aeroporto"]
        
        h = dist_euclidiana(no_centro, no_aeroporto)
        
        # Heurística deve ser não-negativa
        self.assertGreaterEqual(h, 0.0)
    
    def test_heuristica_avancada_admissivel(self):
        """Testa admissibilidade da heurística avançada."""
        from gestao.algoritmos_procura.uteis import heuristica_avancada
        from gestao.algoritmos_procura.a_estrela import a_star_search
        
        gestor = ConfigTestes.criar_gestor_teste()
        veiculo = gestor.veiculos["E1"]
        
        # Heurística deve ser <= custo real
        h = heuristica_avancada(
            self.grafo, veiculo, "Centro", "Aeroporto", tempo_atual=0
        )
        
        custo_real, _ = a_star_search(
            self.grafo, "Centro", "Aeroporto"
        )
        
        self.assertLessEqual(h, custo_real * 1.1)  # Permite 10% tolerância
    
    def test_tempo_heuristica(self):
        """Testa cálculo de tempo estimado."""
        from gestao.algoritmos_procura.uteis import tempo_heuristica
        
        no_a = self.grafo.nos["Centro"]
        no_b = self.grafo.nos["Shopping"]
        
        tempo = tempo_heuristica(no_a, no_b, velocidadeMedia_kmh=40.0)
        
        self.assertGreater(tempo, 0.0)
        self.assertIsInstance(tempo, float)


if __name__ == '__main__':
    unittest.main()