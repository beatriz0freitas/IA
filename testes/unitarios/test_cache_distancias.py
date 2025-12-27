"""
Testes unitários do sistema de cache de distâncias.
"""

import unittest
from gestao.cache_distancias import CacheDistancias
from testes.test_config import ConfigTestes


class TestCacheDistancias(unittest.TestCase):
    """Testa cache de distâncias euclidianas."""
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        self.grafo = ConfigTestes.criar_grafo_teste()
        self.cache = CacheDistancias(self.grafo)
    
    def test_cache_hit(self):
        """Testa que segunda chamada usa cache."""
        # Primeira chamada (cache miss)
        dist1 = self.cache.get_distancia_euclidiana("Centro", "Aeroporto")
        
        # Segunda chamada (cache hit)
        dist2 = self.cache.get_distancia_euclidiana("Centro", "Aeroporto")
        
        self.assertEqual(dist1, dist2)
        
        stats = self.cache.estatisticas()
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 1)
    
    def test_simetria(self):
        """Testa que dist(A,B) = dist(B,A)."""
        dist_ab = self.cache.get_distancia_euclidiana("Centro", "Shopping")
        dist_ba = self.cache.get_distancia_euclidiana("Shopping", "Centro")
        
        self.assertEqual(dist_ab, dist_ba)
        
        # Ambas devem usar o mesmo cache
        stats = self.cache.estatisticas()
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 1)
    
    def test_pre_carregamento(self):
        """Testa pré-carregamento de distâncias críticas."""
        nos_criticos = ["Centro", "Aeroporto", "Hospital"]
        self.cache.pre_carregar_distancias_criticas(nos_criticos)
        
        stats = self.cache.estatisticas()
        # 3 nós = 3 pares (Centro-Aeroporto, Centro-Hospital, Aeroporto-Hospital)
        self.assertEqual(stats['cache_misses'], 3)
    
    def test_limpar_cache(self):
        """Testa limpeza do cache."""
        self.cache.get_distancia_euclidiana("Centro", "Shopping")
        self.cache.limpar_cache()
        
        stats = self.cache.estatisticas()
        self.assertEqual(stats['cache_hits'], 0)
        self.assertEqual(stats['cache_misses'], 0)
        self.assertEqual(stats['tamanho_cache'], 0)


if __name__ == '__main__':
    unittest.main()