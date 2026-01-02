from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from fabrica.pedidos_demo import PedidosDemo

from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador
from gestao.estrategia_selecao import SelecaoDeadMileage
from interface_taxigreen import InterfaceTaxiGreen


def main():
    print("\nInicializar simulação TaxiGreen...\n")

    grafo = GrafoDemo.criar_grafo_demo()
    usar_custo_composto = True

    # Usa estratégia que minimiza km sem passageiros (dead mileage)
    estrategia = SelecaoDeadMileage(penalizacao=2.0)
    gestor = GestorFrota(grafo, estrategia_selecao=estrategia)

    VeiculosDemo.criar_frota_demo(gestor)

    simulador = Simulador(gestor, duracao_total=60, usar_transito=True, usar_falhas=True, prob_falha=0.08, usar_ride_sharing=True)  # 60 min, 8% falhas
    interface = InterfaceTaxiGreen(simulador)
    simulador.interface = interface

    PedidosDemo.criar_pedidos_demo(simulador)
    print(f"\n Modo de custo: {'COMPOSTO (multi-objetivo)' if usar_custo_composto else 'SIMPLES (tempo)'}")
    print(f"\n Pedidos agendados: {len(simulador.fila_pedidos)}")
    print(f" Duração da simulação: {simulador.duracao_total} minutos")
    print(f" Trânsito dinâmico: {'Ativo' if simulador.gestor_transito else 'Desativado'}")
    if simulador.gestor_transito:
        print(f" Hora inicial: {simulador.gestor_transito.hora_inicial:02d}:00 (meia-noite)")
    print(f" Falhas em estações: {'Ativo (prob=8%)' if simulador.gestor_falhas else 'Desativado'}")
    print(f" Ride Sharing: {'Disponível (desativado por padrão)' if simulador.gestor_ride_sharing else 'Desativado'}\n")
    interface.iniciar()


if __name__ == "__main__":
    main()
