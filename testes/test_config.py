"""
Configurações e fixtures compartilhadas entre testes.
"""

import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from gestao.gestor_frota import GestorFrota


class ConfigTestes:
    """Configurações globais para testes."""
    
    # Tolerância para comparações float
    TOLERANCIA_FLOAT = 0.001
    
    # Timeouts
    TIMEOUT_ALGORITMO_MS = 5000
    TIMEOUT_SIMULACAO_S = 60
    
    # Parâmetros de simulação padrão
    DURACAO_SIMULACAO_DEFAULT = 30  # minutos
    NUM_PEDIDOS_TESTE = 10
    
    @staticmethod
    def criar_grafo_teste():
        """Cria grafo padrão para testes."""
        return GrafoDemo.criar_grafo_demo()
    
    @staticmethod
    def criar_gestor_teste():
        """Cria gestor de frota com grafo e veículos."""
        grafo = ConfigTestes.criar_grafo_teste()
        gestor = GestorFrota(grafo)
        VeiculosDemo.criar_frota_demo(gestor)
        return gestor