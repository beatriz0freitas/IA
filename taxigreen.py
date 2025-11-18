"""
TaxiGreen - Sistema de Gestão de Frota de Táxis
Versão refatorizada com correções de imports cíclicos e fluxo de execução
"""

from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from fabrica.pedidos_demo import PedidosDemo

from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador
from interface_taxigreen import InterfaceTaxiGreen


def main():
    print("\n" + "="*50)
    print("Inicializar simulação TaxiGreen...")
    print("="*50 + "\n")

    # 1. Criar grafo urbano
    grafo = GrafoDemo.criar_grafo_demo()
    print(f"✓ Grafo criado com {len(grafo.nos)} nós")

    # 2. Criar gestor de frota COM RIDE-SHARING
    gestor = GestorFrota(grafo, usar_ride_sharing=True)
    print(f"✓ Ride-Sharing: {'ATIVADO' if gestor.usar_ride_sharing else 'DESATIVADO'}")

    # 3. Criar frota de demonstração
    VeiculosDemo.criar_frota_demo(gestor)
    print(f"✓ Frota criada com {len(gestor.veiculos)} veículos")

    # 4. Criar simulador (SEM interface ainda - evita ciclo)
    simulador = Simulador(gestor, duracao_total=12)
    print(f"✓ Simulador criado (duração: 12 minutos)")

    # 5. Criar interface e vincular
    interface = InterfaceTaxiGreen(simulador)
    simulador.set_interface(interface)
    print(f"✓ Interface criada")

    # 6. Agendar pedidos de demonstração
    PedidosDemo.criar_pedidos_demo(simulador)
    print(f"✓ {len(simulador.pedidos_todos)} pedidos agendados")

    print("\n" + "="*50)
    print("Iniciando interface (clique em 'Iniciar Simulação')")
    print("="*50 + "\n")

    # 7. Iniciar GUI (bloqueante)
    interface.iniciar()


if __name__ == "__main__":
    main()