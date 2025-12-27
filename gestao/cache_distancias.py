"""
Sistema de cache para otimizar cálculos repetidos de distâncias.
Reduz complexidade computacional em operações frequentes.
"""

import math
from typing import Dict, Tuple
from modelo.grafo import Grafo

class CacheDistancias:
    """
    Cache para distâncias euclidianas entre nós.
    
    Justificação:
    - Distância euclidiana é calculada centenas de vezes (heurísticas A*)
    - Cálculo envolve sqrt() que é custoso
    - Distâncias são simétricas: dist(A,B) = dist(B,A)
    - Grafo é estático durante simulação
    
    """
    
    def __init__(self, grafo: Grafo):
        self.grafo = grafo
        self._cache: Dict[Tuple[str, str], float] = {}
        self._hits = 0
        self._misses = 0
    
    def get_distancia_euclidiana(self, no1_id: str, no2_id: str) -> float:

        # Cria chave simétrica (ordem alfabética)
        key = tuple(sorted([no1_id, no2_id]))
        
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        
        # Cache miss - calcula
        self._misses += 1
        no1 = self.grafo.nos[no1_id]
        no2 = self.grafo.nos[no2_id]
        
        distancia = math.hypot(
            no1.posicaox - no2.posicaox,
            no1.posicaoy - no2.posicaoy
        )
        
        self._cache[key] = distancia
        return distancia
    
    def pre_carregar_distancias_criticas(self, nos_criticos: list[str]):
        """
        Pré-carrega distâncias entre nós mais usados (ex: estações).
        Chamado uma vez na inicialização.
        """
        for i, no1 in enumerate(nos_criticos):
            for no2 in nos_criticos[i+1:]:
                self.get_distancia_euclidiana(no1, no2)
    
    def limpar_cache(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def estatisticas(self) -> dict:
        """Retorna estatísticas de uso do cache."""
        total = self._hits + self._misses
        taxa_acerto = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "cache_hits": self._hits,
            "cache_misses": self._misses,
            "taxa_acerto": round(taxa_acerto, 1),
            "tamanho_cache": len(self._cache)
        }


class CacheRotas:
    """
    Cache para rotas completas calculadas.
    
    Só funciona se trânsito for estático.
    Se usar trânsito dinâmico, este cache deve ser invalidado periodicamente.
    """
    
    def __init__(self, validade_minutos: int = 10):
        self._cache: Dict[Tuple[str, str, str], Tuple[list, float, int]] = {}
        self.validade_minutos = validade_minutos
        self._hits = 0
        self._misses = 0
    
    def get_rota(self, origem: str, destino: str, algoritmo: str, 
                 tempo_atual: int) -> Tuple[list, float] | None:
        """
        Returns:
            (caminho, custo) se encontrado e válido, None caso contrário
        """
        key = (origem, destino, algoritmo)
        
        if key in self._cache:
            caminho, custo, tempo_calculo = self._cache[key]
            
            # Verifica validade (importante com trânsito dinâmico)
            if tempo_atual - tempo_calculo < self.validade_minutos:
                self._hits += 1
                return caminho, custo
        
        self._misses += 1
        return None
    
    def armazenar_rota(self, origem: str, destino: str, algoritmo: str,
                       caminho: list, custo: float, tempo_atual: int):
        """Armazena rota calculada no cache."""
        key = (origem, destino, algoritmo)
        self._cache[key] = (caminho, custo, tempo_atual)
    
    def invalidar_por_tempo(self, tempo_atual: int):
        """Remove rotas expiradas."""
        keys_remover = [
            key for key, (_, _, tempo_calc) in self._cache.items()
            if tempo_atual - tempo_calc >= self.validade_minutos
        ]
        
        for key in keys_remover:
            del self._cache[key]
    
    def limpar_cache(self):
        """Limpa cache completamente."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def estatisticas(self) -> dict:
        """Retorna estatísticas de uso."""
        total = self._hits + self._misses
        taxa_acerto = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "cache_hits": self._hits,
            "cache_misses": self._misses,
            "taxa_acerto": round(taxa_acerto, 1),
            "rotas_cacheadas": len(self._cache)
        }