
from modelo.grafo import Grafo, No, TipoNo
from modelo.veiculos import VeiculoEletrico, VeiculoCombustao, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador


def construir_grafo_teste() -> Grafo:
    g = Grafo()
    # Nós: 3 zonas de recolha + 1 estação elétrica + 1 posto de combustível
    g.adiciona_no(No("A", 0, 0, TipoNo.RECOLHA_PASSAGEIROS))
    g.adiciona_no(No("B", 1, 0, TipoNo.RECOLHA_PASSAGEIROS))
    g.adiciona_no(No("C", 0, 1, TipoNo.RECOLHA_PASSAGEIROS))
    g.adiciona_no(No("RECARGA", 2, 0, TipoNo.ESTACAO_RECARGA))
    g.adiciona_no(No("POSTO", -1, 0, TipoNo.POSTO_ABASTECIMENTO))

    # Ligações simples
    g.adiciona_aresta("A", "B", 5, 10)
    g.adiciona_aresta("A", "C", 4, 8)
    g.adiciona_aresta("B", "RECARGA", 3, 6)
    g.adiciona_aresta("C", "POSTO", 3, 7)
    g.adiciona_aresta("B", "C", 2, 4)
    return g


def criar_frota_teste(gestor: GestorFrota):
    # Um elétrico e um a combustão
    v1 = VeiculoEletrico(
        id_veiculo="E1",
        posicao="A",
        autonomia_km=15,
        autonomiaMax_km=15,
        capacidade_passageiros=4,
        custo_km=0.10,
        estado=EstadoVeiculo.DISPONIVEL,
        km_total=0,
        id_rota="r1",
        rota=["ee","ss"],
        tempo_recarregamento_min=10,
        capacidade_bateria_kWh=40,
        consumo_kWh_km=0.15

    )

    v2 = VeiculoCombustao(
        id_veiculo="C1",
        posicao="B",
        autonomia_km=30,
        autonomiaMax_km=30,
        capacidade_passageiros=4,
        custo_km=0.20,
        estado=EstadoVeiculo.DISPONIVEL,
        km_total=0,
        id_rota="r4",
        rota=["rr","tt"],
        tempo_reabastecimento_min=5,
        emissao_CO2_km=0.12
    )

    gestor.adicionar_veiculo(v1)
    gestor.adicionar_veiculo(v2)


def criar_pedidos_teste(simulador: Simulador):
    # Pedido elétrico imediato
    p1 = Pedido(
        id_pedido="P1",
        posicao_inicial="A",
        posicao_destino="B",
        passageiros=2,
        instante_pedido=0,
        prioridade=2,
        pref_ambiental="eletrico",
        estado=EstadoPedido.PENDENTE,
        veiculo_atribuido="v1",
        instante_atendimento=None
    )

    # Pedido combustão no tempo 2
    p2 = Pedido(
        id_pedido="P2",
        posicao_inicial="C",
        posicao_destino="POSTO",
        passageiros=1,
        instante_pedido=2,
        pref_ambiental="combustao",
        prioridade=1,
        estado=EstadoPedido.PENDENTE,
        veiculo_atribuido="v3",
        instante_atendimento=4
    )

    simulador.agendar_pedido(p1)
    simulador.agendar_pedido(p2)


def main():
    print("\n🚦 Inicializando teste TaxiGreen...\n")

    grafo = construir_grafo_teste()
    gestor = GestorFrota(grafo)
    criar_frota_teste(gestor)

    simulador = Simulador(gestor, duracao_total=10)
    criar_pedidos_teste(simulador)

    simulador.executar()


if __name__ == "__main__":
    main()
