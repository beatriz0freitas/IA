"""
TaxiGreen - Sistema de Gestão Inteligente de Frota
Versão com janelas de configuração pré-simulação.
"""

from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from fabrica.pedidos_demo import PedidosDemo

from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador
from gestao.estrategia_selecao import (
    SelecaoMenorDistancia, SelecaoCustoComposto, 
    SelecaoDeadMileage, SelecaoEquilibrada, SelecaoPriorizarEletricos
)
from gestao.funcao_custo import FuncaoCustoComposta
from interface.interface_taxigreen import InterfaceTaxiGreen
from interface.janela_configuracao import obter_configuracoes_simulacao


def criar_estrategia(nome: str):
    """Factory para criar estratégia de seleção."""
    if nome == 'menor_distancia':
        return SelecaoMenorDistancia()
    if nome == 'custo_composto':
        return SelecaoCustoComposto(FuncaoCustoComposta())
    if nome == 'equilibrada':
        return SelecaoEquilibrada()
    if nome == 'priorizar_eletricos':
        return SelecaoPriorizarEletricos()
    
    # default
    return SelecaoDeadMileage(penalizacao=2.0)

def carregar_pedidos(simulador, grafo, config):
    """
    Carrega pedidos no simulador de acordo com a configuração.
    """
    if config['tipo_pedidos'] == 'demo':
        PedidosDemo.criar_pedidos_demo(simulador)
        return len(simulador.fila_pedidos)

    # Pedidos aleatórios
    zonas_validas = [
        no_id for no_id, no in grafo.nos.items()
        if no.tipo.name == 'RECOLHA_PASSAGEIROS'
    ]

    simulador.gerar_pedidos_aleatorios(
        config['num_pedidos'],
        zonas_validas
    )
    return config['num_pedidos']

def main():
    print("\n" + "=" * 60)
    print("TaxiGreen - Sistema de Gestão Inteligente de Frota")
    print("=" * 60 + "\n")

    # === CONFIGURAÇÃO ===
    config = obter_configuracoes_simulacao()
    if not config:
        print("Configuração cancelada. Encerrando...")
        return

    # === RELATÓRIO DE CONFIGURAÇÃO ===
    print("CONFIGURAÇÃO DA SIMULAÇÃO")
    print("-" * 60)
    print(f"Duração: {config['duracao']} minutos")
    print(f"Hora inicial: {config['hora_inicial']}:00")
    print(f"Algoritmo de planeamento: {config['algoritmo'].upper()}")
    print(f"Estratégia de seleção: {config['estrategia'].replace('_', ' ').title()}")
    print(f"Trânsito dinâmico: {'✓' if config['usar_transito'] else '✗'}")
    print(f"Sistema de falhas: {'✓' if config['usar_falhas'] else '✗'}")
    if config['usar_falhas']:
        print(f"   └─ Probabilidade: {config['prob_falha'] * 100:.0f}%")

    print("\nFEATURES AVANÇADAS")
    print("-" * 60)
    print(f"Reposicionamento proativo: {'✓' if config['reposicionamento'] else '✗'}")
    print(f"Ride Sharing: {'✓' if config['ride_sharing'] else '✗'}")
    if config['ride_sharing']:
        print(f"   ├─ Raio: {config['raio_agrupamento']} km")
        print(f"   └─ Janela: {config['janela_temporal']} min")

    print(f"\nPedidos: {config['tipo_pedidos'].upper()}")
    print("=" * 60 + "\n")

    # === CRIAÇÃO DO SISTEMA ===
    grafo = GrafoDemo.criar_grafo_demo()
    estrategia = criar_estrategia(config['estrategia'])

    gestor = GestorFrota(grafo, estrategia_selecao=estrategia)
    gestor.definir_algoritmo_procura(config['algoritmo'])
    VeiculosDemo.criar_frota_demo(gestor)

    simulador = Simulador(
        gestor,
        duracao_total=config['duracao'],
        usar_transito=config['usar_transito'],
        usar_falhas=config['usar_falhas'],
        prob_falha=config['prob_falha'],
        usar_ride_sharing=config['ride_sharing'],
        velocidade=config['velocidade']
    )

    # Aplica configuração centralizada
    simulador.configurar(config)

    # Interface
    interface = InterfaceTaxiGreen(simulador, config)
    simulador.interface = interface

    # === PEDIDOS ===
    total = carregar_pedidos(simulador, grafo, config)
    print(f"✓ {total} pedidos carregados")

    print("\n▶️  Iniciando interface gráfica...\n")
    interface.iniciar()


if __name__ == "__main__":
    main()