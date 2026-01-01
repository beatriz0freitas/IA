"""
Testes Unitários - Cache de Rotas
"""

import unittest
from gestao.cache_distancias import CacheRotas
from testes.test_config import ConfigTestes


class TestCacheRotas(unittest.TestCase):
    """Testa sistema de cache de rotas completas."""
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        self.cache = CacheRotas(validade_minutos=10)
    
    def test_armazenar_e_recuperar(self):
        """Testa armazenamento e recuperação de rota."""
        caminho = ["Centro", "Shopping", "Aeroporto"]
        custo = 15.5
        
        # Armazena
        self.cache.armazenar_rota(
            "Centro", "Aeroporto", "astar", 
            caminho, custo, tempo_atual=5
        )
        
        # Recupera
        resultado = self.cache.get_rota(
            "Centro", "Aeroporto", "astar", tempo_atual=7
        )
        
        self.assertIsNotNone(resultado)
        caminho_cache, custo_cache = resultado
        self.assertEqual(caminho_cache, caminho)
        self.assertEqual(custo_cache, custo)
    
    def test_expiracao_por_tempo(self):
        """Testa expiração de rotas antigas."""
        caminho = ["A", "B", "C"]
        
        # Armazena no tempo 0
        self.cache.armazenar_rota(
            "A", "C", "astar", caminho, 10.0, tempo_atual=0
        )
        
        # Tenta recuperar após validade (tempo 15 > validade 10)
        resultado = self.cache.get_rota(
            "A", "C", "astar", tempo_atual=15
        )
        
        # Deve retornar None (expirou)
        self.assertIsNone(resultado)
    
    def test_algoritmos_diferentes(self):
        """Testa que rotas são separadas por algoritmo."""
        caminho_astar = ["A", "B", "C"]
        caminho_ucs = ["A", "D", "C"]
        
        self.cache.armazenar_rota("A", "C", "astar", caminho_astar, 10.0, 0)
        self.cache.armazenar_rota("A", "C", "ucs", caminho_ucs, 12.0, 0)
        
        # Recupera com algoritmos diferentes
        rota_astar = self.cache.get_rota("A", "C", "astar", 1)
        rota_ucs = self.cache.get_rota("A", "C", "ucs", 1)
        
        self.assertNotEqual(rota_astar[0], rota_ucs[0])
    
    def test_invalidar_expirados(self):
        """Testa remoção de rotas expiradas."""
        # Armazena 3 rotas
        self.cache.armazenar_rota("A", "B", "astar", ["A", "B"], 5.0, 0)
        self.cache.armazenar_rota("B", "C", "astar", ["B", "C"], 6.0, 5)
        self.cache.armazenar_rota("C", "D", "astar", ["C", "D"], 7.0, 12)
        
        # Invalida no tempo 20 (validade = 10)
        self.cache.invalidar_por_tempo(tempo_atual=20)
        
        stats = self.cache.estatisticas()
        # Apenas a última rota (tempo 12) deve permanecer
        self.assertEqual(stats['rotas_cacheadas'], 1)
    
    def test_estatisticas_hits_misses(self):
        """Testa contabilização de hits/misses."""
        self.cache.armazenar_rota("A", "B", "astar", ["A", "B"], 5.0, 0)
        
        # Hit
        self.cache.get_rota("A", "B", "astar", 1)
        
        # Miss
        self.cache.get_rota("X", "Y", "astar", 1)
        
        stats = self.cache.estatisticas()
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 1)
        self.assertEqual(stats['taxa_acerto'], 50.0)
    
    def test_limpar_cache(self):
        """Testa limpeza completa do cache."""
        self.cache.armazenar_rota("A", "B", "astar", ["A", "B"], 5.0, 0)
        self.cache.armazenar_rota("B", "C", "ucs", ["B", "C"], 6.0, 0)
        
        self.cache.limpar_cache()
        
        stats = self.cache.estatisticas()
        self.assertEqual(stats['rotas_cacheadas'], 0)
        self.assertEqual(stats['cache_hits'], 0)
        self.assertEqual(stats['cache_misses'], 0)


if __name__ == '__main__':
    unittest.main()