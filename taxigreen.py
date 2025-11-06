from modelo.veiculos import VeiculoEletrico
from modelo.grafo import Grafo
from gestao.gestor_frota import GestorFrota
from gestao.metricas import Metricas
from gestao.simulador import Simulador

def smoke_test():
    g = Grafo()
    g.adiciona_no("A", "zona", "ESTACAO_RECARGA")
    g.adiciona_no("B", "zona", "POSTO_ABASTECIMENTO")
    g.adiciona_aresta("A", "B", 5.0, 10)

    m = Metricas()
    gestor = GestorFrota(g, m)
    v = VeiculoEletrico("E1", "A", 80, 100, 4, 0.2, 20, 50, 0.2)
    gestor.adicionar_veiculo(v)

    s = Simulador(gestor, duracao_total=5)
    s.executar()

if __name__ == "__main__":
    smoke_test()
