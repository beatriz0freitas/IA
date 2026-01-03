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
    estrategias = {
        'menor_distancia': SelecaoMenorDistancia(),
        'custo_composto': SelecaoCustoComposto(FuncaoCustoComposta()),
        'dead_mileage': SelecaoDeadMileage(penalizacao=2.0),
        'equilibrada': SelecaoEquilibrada(),
        'priorizar_eletricos': SelecaoPriorizarEletricos()
    }
    
    return estrategias.get(nome, SelecaoDeadMileage(penalizacao=2.0))


def main():
    print("\n" + "="*60)
    print("TaxiGreen - Sistema de Gestão Inteligente de Frota")
    print("="*60 + "\n")
    
    # === JANELAS DE CONFIGURAÇÃO ===
    config = obter_configuracoes_simulacao()
    
    if not config:
        print("Configuração cancelada. Encerrando...")
        return
    
    # === RELATÓRIO DE CONFIGURAÇÃO ===
    print("\nCONFIGURAÇÃO DA SIMULAÇÃO")
    print("-" * 60)
    print(f"Duração: {config['duracao']} minutos")
    print(f"Hora inicial: {config['hora_inicial']}:00")
    print(f"Algoritmo: {config['algoritmo'].upper()}")
    print(f"Estratégia: {config['estrategia'].replace('_', ' ').title()}")
    print(f"Trânsito dinâmico: {'✓ Ativo' if config['usar_transito'] else '✗ Desativado'}")
    print(f"Sistema de falhas: {'✓ Ativo' if config['usar_falhas'] else '✗ Desativado'}")
    if config['usar_falhas']:
        print(f"   └─ Probabilidade: {config['prob_falha']*100:.0f}%")
    
    print("\n FEATURES AVANÇADAS")
    print("-" * 60)
    print(f"Reposicionamento proativo: {'✓ Ativo' if config['reposicionamento'] else '✗ Desativado'}")
    print(f"Ride Sharing: {'✓ Ativo' if config['ride_sharing'] else '✗ Desativado'}")
    if config['ride_sharing']:
        print(f"   ├─ Raio agrupamento: {config['raio_agrupamento']} km")
        print(f"   └─ Janela temporal: {config['janela_temporal']} min")
    
    print(f"\nPedidos: {config['tipo_pedidos'].upper()}")
    if config['tipo_pedidos'] == 'aleatorios':
        print(f"   └─ Quantidade: {config['num_pedidos']}")
    print("="*60 + "\n")
    
    # === CRIAÇÃO DO SISTEMA ===
    print("Inicializando sistema...\n")
    
    grafo = GrafoDemo.criar_grafo_demo()
    estrategia = criar_estrategia(config['estrategia'])
    gestor = GestorFrota(grafo, estrategia_selecao=estrategia)
    gestor.definir_algoritmo_procura(config['algoritmo'])
    VeiculosDemo.criar_frota_demo(gestor)
    
    # Simulador
    simulador = Simulador(
        gestor, 
        duracao_total=config['duracao'],
        usar_transito=config['usar_transito'],
        usar_falhas=config['usar_falhas'],
        prob_falha=config['prob_falha'],
        usar_ride_sharing=config['ride_sharing']
    )
    
    # Configura hora inicial
    if simulador.gestor_transito:
        simulador.gestor_transito.hora_inicial = config['hora_inicial']
        simulador.gestor_transito.hora_atual = config['hora_inicial']
    
    # Configura Ride Sharing
    if simulador.gestor_ride_sharing:
        simulador.gestor_ride_sharing.raio_agrupamento = config['raio_agrupamento']
        simulador.gestor_ride_sharing.janela_temporal = config['janela_temporal']
    
    # Interface (passa config como parâmetro)
    interface = InterfaceTaxiGreen(simulador, config)
    simulador.interface = interface
    
    # === GERAÇÃO DE PEDIDOS ===
    if config['tipo_pedidos'] == 'demo':
        PedidosDemo.criar_pedidos_demo(simulador)
        print(f"✓ {len(simulador.fila_pedidos)} pedidos demo carregados")
    else:
        # Pedidos aleatórios
        zonas_validas = [
            no_id for no_id, no in grafo.nos.items()
            if no.tipo.name == 'RECOLHA_PASSAGEIROS'
        ]
        simulador.gerar_pedidos_aleatorios(
            config['num_pedidos'], 
            zonas_validas
        )
        print(f"✓ {config['num_pedidos']} pedidos aleatórios gerados")
    
    print(f"✓ Sistema configurado com sucesso!\n")
    print("="*60)
    print("▶️  Iniciando interface gráfica...")
    print("="*60 + "\n")
    
    interface.iniciar()

if __name__ == "__main__":
    main()