"""
Script para testar e comparar algoritmos de procura.
"""

from fabrica.grafo_demo import GrafoDemo
from gestao.comparador_algoritmos import ComparadorAlgoritmos
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs


def main():
    print("\n🔍 TESTE DE COMPARAÇÃO DE ALGORITMOS\n")

    # Cria grafo de demonstração
    grafo = GrafoDemo.criar_grafo_demo()

    # Define algoritmos a testar
    algoritmos = {
        "A*": a_star_search,
        "UCS": uniform_cost_search,
        "BFS": bfs,
        "DFS": dfs
    }

    # Cria comparador
    comparador = ComparadorAlgoritmos(grafo)

    # Casos de teste
    casos_teste = [
        ("Centro", "Shopping", "Caso 1: Curta distância (centro)"),
        ("Centro", "Aeroporto", "Caso 2: Média distância (centro-aeroporto)"),
        ("Porto", "Escola_Norte", "Caso 3: Longa distância (sul-norte)"),
        ("Suburbio_Oeste1", "Parque_Tec", "Caso 4: Travessia completa (oeste-este)"),
    ]

    for origem, destino, descricao in casos_teste:
        print(f"\n{'='*80}")
        print(f"{descricao}: {origem} → {destino}")
        print(f"{'='*80}")

        resultados = comparador.comparar_multiplos(algoritmos, origem, destino)

        print(comparador.gerar_relatorio_texto())


if __name__ == "__main__":
    main()
