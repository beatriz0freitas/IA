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

    simulador = Simulador(gestor, duracao_total=60)  # 60 minutos = 1 hora
    interface = InterfaceTaxiGreen(simulador)
    simulador.interface = interface

    PedidosDemo.criar_pedidos_demo(simulador)

    print(f"\n Pedidos agendados: {len(simulador.fila_pedidos)}")
    print(f" Duração da simulação: {simulador.duracao_total} minutos")
    print(f" Trânsito dinâmico: {'Ativo' if simulador.gestor_transito else 'Desativado'}")
    print(f" Falhas em estações: {'Ativo (prob=15%)' if simulador.gestor_falhas else 'Desativado'}\n")

    interface.iniciar()


if __name__ == "__main__":
    main()
