"""
Fábrica de grafos de demonstração para a simulação TaxiGreen.

Contém uma função que constrói um grafo urbano completo
com nós de diferentes tipos (recolha, recarga, abastecimento)
e arestas bidirecionais com distâncias realistas.
"""

from modelo.grafo import Grafo, No, TipoNo

class GrafoDemo:
    def criar_grafo_demo() -> Grafo:
        g = Grafo()

        cordenadas = {
            "A": (0, 1, TipoNo.RECOLHA_PASSAGEIROS),
            "B": (1, 2, TipoNo.RECOLHA_PASSAGEIROS),
            "C": (1, 0, TipoNo.POSTO_ABASTECIMENTO),
            "D": (2, 1, TipoNo.ESTACAO_RECARGA),
            "E": (3, 2, TipoNo.RECOLHA_PASSAGEIROS),
            "F": (3, 0, TipoNo.ESTACAO_RECARGA),
            "G": (4, 1, TipoNo.RECOLHA_PASSAGEIROS),
            "H": (5, 2, TipoNo.POSTO_ABASTECIMENTO),
            "I": (5, 0, TipoNo.RECOLHA_PASSAGEIROS),
            "J": (6, 1, TipoNo.RECOLHA_PASSAGEIROS),
            "K": (4, 3, TipoNo.ESTACAO_RECARGA),
            "L": (2, 3, TipoNo.RECOLHA_PASSAGEIROS),
        }

        for nid, (x, y, tipo) in cordenadas.items():
            g.adiciona_no(No(nid, x, y, tipo))

        conexoes = [
            ("A", "B", 1.0), ("A", "C", 1.2), ("A", "D", 2.0),
            ("B", "D", 1.5), ("B", "E", 2.0), ("C", "D", 1.8),
            ("C", "F", 2.2), ("D", "E", 1.3), ("D", "F", 1.6),
            ("D", "G", 2.0), ("E", "H", 2.2), ("E", "G", 1.5),
            ("F", "G", 1.4), ("F", "I", 2.3), ("G", "H", 1.8),
            ("G", "I", 2.0), ("G", "J", 2.5), ("H", "J", 2.0),
            ("I", "J", 2.2), ("H", "K", 1.5), ("B", "L", 1.8), 
            ("E", "L", 1.6)
        ]
        for origem, destino, dist in conexoes:
            g.adiciona_aresta(origem, destino, dist, tempoViagem_min=dist * 2.5)

        return g
