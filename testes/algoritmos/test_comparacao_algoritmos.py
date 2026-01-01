"""
Testes de comparação entre algoritmos de procura.
"""

import unittest
from gestao.comparador_algoritmos import ComparadorAlgoritmos, CenarioTeste
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs
from gestao.algoritmos_procura.greedy import greedy
from testes.test_config import ConfigTestes


class TestComparacaoAlgoritmos(unittest.TestCase):
    
    def setUp(self):
        self.grafo = ConfigTestes.criar_grafo_teste()
        self.comparador = ComparadorAlgoritmos(self.grafo)
        
        self.algoritmos = {
            "A*": a_star_search,
            "Greedy": greedy,
            "UCS": uniform_cost_search,
            "BFS": bfs,
            "DFS": dfs
        }
    
    def test_cenario_curta_distancia(self):
        """Testa cenário de curta distância."""
        cenario = CenarioTeste(
            nome="Curta distância",
            origem="Centro",
            destino="Shopping",
            descricao="Teste básico de curta distância"
        )
        
        resultados = self.comparador.comparar_multiplos(self.algoritmos, cenario)
        
        # Todos devem encontrar solução
        self.assertEqual(len(resultados), 5)
        for r in resultados:
            self.assertTrue(r.sucesso, f"{r.nome_algoritmo} falhou")
    
    def test_astar_e_otimo(self):
        """Verifica que A* encontra solução ótima."""
        cenario = CenarioTeste(
            nome="Teste otimalidade",
            origem="Centro",
            destino="Aeroporto",
            descricao="Verifica se A* é ótimo"
        )
        
        resultados = self.comparador.comparar_multiplos(self.algoritmos, cenario)
        
        # A* e UCS devem ter mesmo custo (ambos ótimos)
        resultado_astar = next(r for r in resultados if r.nome_algoritmo == "A*")
        resultado_ucs = next(r for r in resultados if r.nome_algoritmo == "UCS")
        
        self.assertAlmostEqual(
            resultado_astar.custo_solucao,
            resultado_ucs.custo_solucao,
            delta=1.0
        )


if __name__ == '__main__':
    unittest.main()