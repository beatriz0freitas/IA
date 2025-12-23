"""
Script para testar e comparar algoritmos de procura.
"""

from fabrica.grafo_demo import GrafoDemo
from gestao.comparador_algoritmos import ComparadorAlgoritmos
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs
from gestao.gestor_frota import GestorFrota
from fabrica.veiculos_demo import VeiculosDemo


def comparar_heuristicas():
    """
    Compara A* com heurística simples vs avançada
    """
    print("\n" + "="*80)
    print("COMPARAÇÃO: A* Simples vs A* Avançado")
    print("="*80)
    
    grafo = GrafoDemo.criar_grafo_demo()
    gestor = GestorFrota(grafo)
    VeiculosDemo.criar_frota_demo(gestor)
    
    veiculo = gestor.veiculos["E1"]
    veiculo.autonomia_km = 30  # Baixa autonomia para testar penalização
    
    casos = [
        ("Centro", "Aeroporto", "Longa distância com baixa autonomia"),
        ("Centro", "Shopping", "Curta distância"),
    ]
    
    for origem, destino, descricao in casos:
        print(f"\n{descricao}: {origem} → {destino}")
        print(f"Autonomia veículo: {veiculo.autonomia_km:.1f} km")
        
        # A* com heurística simples
        inicio = time.time()
        custo_simples, caminho_simples = a_star_search(
            grafo, origem, destino, 
            veiculo=None,  # Sem veículo = heurística simples
            usar_heuristica_avancada=False
        )
        tempo_simples = (time.time() - inicio) * 1000
        
        # A* com heurística avançada
        inicio = time.time()
        custo_avancado, caminho_avancado = a_star_search(
            grafo, origem, destino,
            veiculo=veiculo,
            tempo_atual=480,  # 8h da manhã (rush hour)
            usar_heuristica_avancada=True
        )
        tempo_avancado = (time.time() - inicio) * 1000
        
        print(f"\n  A* Simples:")
        print(f"    Tempo: {tempo_simples:.3f} ms")
        print(f"    Custo: {custo_simples:.2f} min")
        print(f"    Caminho: {len(caminho_simples)} nós")
        
        print(f"\n  A* Avançado:")
        print(f"    Tempo: {tempo_avancado:.3f} ms")
        print(f"    Custo: {custo_avancado:.2f} min")
        print(f"    Caminho: {len(caminho_avancado)} nós")
        
        print(f"\n  Diferença:")
        print(f"    Custo: {abs(custo_avancado - custo_simples):.2f} min")
        print(f"    Nós: {abs(len(caminho_avancado) - len(caminho_simples))}")

if __name__ == "__main__":
    comparar_heuristicas()

def main():
    print("\n TESTE DE COMPARAÇÃO DE ALGORITMOS\n")

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