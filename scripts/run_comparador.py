from fabrica.grafo_demo import GrafoDemo
from gestao.algoritmos_procura.bfs import bfs
from gestao.algoritmos_procura.dfs import dfs
from gestao.algoritmos_procura.ucs import uniform_cost_search
from gestao.algoritmos_procura.a_estrela import a_star_search
from gestao.algoritmos_procura.greedy import greedy
from gestao.comparador_algoritmos import ComparadorAlgoritmos, CenarioTeste

# 1. Carregar ou montar o grafo
g = GrafoDemo.criar_grafo_demo()# caso não exista, usar carregamento real

# 2. Instanciar comparador
comparador = ComparadorAlgoritmos(g)

# 3. Definir cenário
cenario = CenarioTeste(
    nome="Centro → Aeroporto",
    origem="Centro",
    destino="Aeroporto",
    descricao="Trajeto comum"
)


# 4. Registrar algoritmos
algos = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": uniform_cost_search,
    "A*": a_star_search,
    'Greedy': greedy
}

# 5. Rodar
resultados = comparador.comparar_multiplos(algos, cenario)

# 6. Mostrar relatório
print(comparador.gerar_relatorio_texto())
