from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from fabrica.pedidos_demo import PedidosDemo

from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador
from interface_taxigreen import InterfaceTaxiGreen


def main():
    print("\nInicializar simulação TaxiGreen...\n")

    grafo = GrafoDemo.criar_grafo_demo()
    gestor = GestorFrota(grafo)

    # Criação da frota e pedidos
    VeiculosDemo.criar_frota_demo(gestor)

    simulador = Simulador(gestor, duracao_total=12)
    interface = InterfaceTaxiGreen(simulador)
    simulador.interface = interface

    PedidosDemo.criar_pedidos_demo(simulador)

    interface.iniciar()


if __name__ == "__main__":
    main()
