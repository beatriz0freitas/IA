"""
Script de teste do algoritmo de Ride-Sharing
Compara desempenho com e sem ride-sharing
"""

from fabrica.grafo_demo import GrafoDemo
from fabrica.veiculos_demo import VeiculosDemo
from fabrica.pedidos_demo import PedidosDemo

from gestao.gestor_frota import GestorFrota
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido


def criar_pedidos_teste(simulador):
    """Cria conjunto maior de pedidos para testar ride-sharing"""
    
    # Agrupar pedidos por origem/destino próximos
    pedidos_teste = [
        Pedido(
            id_pedido="P1",
            posicao_inicial="A",
            posicao_destino="K",
            passageiros=2,
            instante_pedido=0,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        ),
        Pedido(
            id_pedido="P2",
            posicao_inicial="A",
            posicao_destino="E",
            passageiros=1,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        ),
        Pedido(
            id_pedido="P3",
            posicao_inicial="C",
            posicao_destino="D",
            passageiros=1,
            instante_pedido=1,
            prioridade=1,
            pref_ambiental="combustao",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        ),
        Pedido(
            id_pedido="P4",
            posicao_inicial="C",
            posicao_destino="G",
            passageiros=2,
            instante_pedido=1,
            prioridade=2,
            pref_ambiental="combustao",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        ),
        Pedido(
            id_pedido="P5",
            posicao_inicial="B",
            posicao_destino="H",
            passageiros=1,
            instante_pedido=2,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        ),
    ]
    
    for p in pedidos_teste:
        simulador.agendar_pedido(p)


def testar_configuracao(usar_ride_sharing: bool) -> Dict:
    """Testa simulação com configuração específica"""
    
    print(f"\n{'='*60}")
    print(f"TESTE: Ride-Sharing {'ATIVADO' if usar_ride_sharing else 'DESATIVADO'}")
    print(f"{'='*60}\n")
    
    # Criar grafo
    grafo = GrafoDemo.criar_grafo_demo()
    
    # Criar gestor COM ou SEM ride-sharing
    gestor = GestorFrota(grafo, usar_ride_sharing=usar_ride_sharing)
    
    # Criar frota
    VeiculosDemo.criar_frota_demo(gestor)
    
    # Criar simulador
    simulador = Simulador(gestor, duracao_total=20)
    
    # Agendar pedidos de teste
    criar_pedidos_teste(simulador)
    
    print(f"Pedidos agendados: {len(simulador.pedidos_todos)}")
    
    # Executar simulação (sem interface gráfica)
    print(f"\nExecutando simulação...")
    simulador.executar()
    
    # Coletar métricas
    metricas = gestor.metricas.calcular_metricas()
    
    # Calcular ocupação média se ride-sharing ativo
    ocupacao_media = 0.0
    if gestor.ride_sharing:
        ocupacao_media = gestor.ride_sharing.registar_ocupacao()
        relatorio_rs = gestor.ride_sharing.gerar_relatorio()
    
    print(f"\n{'='*60}")
    print(f"RESULTADOS:")
    print(f"{'='*60}")
    print(f"Pedidos concluídos: {metricas['pedidos_servicos']}")
    print(f"Pedidos rejeitados: {metricas['pedidos_rejeitados']}")
    print(f"Taxa de sucesso: {metricas['taxa_sucesso']*100:.1f}%")
    print(f"Custo total: €{metricas['custo_total']:.2f}")
    print(f"Emissões: {metricas['emissoes_totais']:.3f} kg CO2")
    print(f"Km totais: {metricas['km_totais']:.1f}")
    
    if gestor.ride_sharing:
        print(f"\nRide-Sharing:")
        print(f"Grupos ativos: {relatorio_rs['grupos_ativos']}")
        print(f"Passageiros agrupados: {relatorio_rs['total_passageiros_agrupados']}")
        print(f"Ocupação média: {relatorio_rs['ocupacao_media']*100:.1f}%")
        print(f"Eficiência: {relatorio_rs['eficiencia']}")
    
    return {
        "ride_sharing": usar_ride_sharing,
        "metricas": metricas,
        "ocupacao": ocupacao_media if gestor.ride_sharing else 0.0
    }


def comparar_resultados(resultado_sem: Dict, resultado_com: Dict):
    """Compara resultados com e sem ride-sharing"""
    print(f"\n{'='*60}")
    print(f"COMPARAÇÃO: SEM vs COM Ride-Sharing")
    print(f"{'='*60}\n")
    
    print(f"{'Métrica':<25} {'SEM':<15} {'COM':<15} {'Melhoria'}")
    print(f"{'-'*70}")
    
    # Custo
    custo_sem = resultado_sem['metricas']['custo_total']
    custo_com = resultado_com['metricas']['custo_total']
    melhoria_custo = ((custo_sem - custo_com) / custo_sem * 100) if custo_sem > 0 else 0
    print(f"{'Custo (€)':<25} {custo_sem:<15.2f} {custo_com:<15.2f} {melhoria_custo:+.1f}%")
    
    # Emissões
    emis_sem = resultado_sem['metricas']['emissoes_totais']
    emis_com = resultado_com['metricas']['emissoes_totais']
    melhoria_emis = ((emis_sem - emis_com) / emis_sem * 100) if emis_sem > 0 else 0
    print(f"{'Emissões (kg CO2)':<25} {emis_sem:<15.3f} {emis_com:<15.3f} {melhoria_emis:+.1f}%")
    
    # KM
    km_sem = resultado_sem['metricas']['km_totais']
    km_com = resultado_com['metricas']['km_totais']
    melhoria_km = ((km_sem - km_com) / km_sem * 100) if km_sem > 0 else 0
    print(f"{'KM totais':<25} {km_sem:<15.1f} {km_com:<15.1f} {melhoria_km:+.1f}%")
    
    # Taxa sucesso
    taxa_sem = resultado_sem['metricas']['taxa_sucesso']
    taxa_com = resultado_com['metricas']['taxa_sucesso']
    print(f"{'Taxa sucesso (%)':<25} {taxa_sem*100:<15.1f} {taxa_com*100:<15.1f} {'✓' if taxa_com >= taxa_sem else '✗'}")
    
    print(f"\n{'Conclusão:':<25}", end=" ")
    if custo_com < custo_sem and emis_com < emis_sem:
        print("✓ Ride-sharing REDUZ custo e emissões!")
    elif taxa_com > taxa_sem:
        print("✓ Ride-sharing MELHORA taxa de sucesso!")
    else:
        print("~ Resultados similares ou ride-sharing menos eficiente neste teste")


if __name__ == "__main__":
    from typing import Dict
    
    print("\n" + "#"*60)
    print("# TESTE DE RIDE-SHARING - TaxiGreen")
    print("#"*60)
    
    # Teste SEM ride-sharing
    resultado_sem = testar_configuracao(usar_ride_sharing=False)
    
    # Teste COM ride-sharing
    resultado_com = testar_configuracao(usar_ride_sharing=True)
    
    # Comparar
    comparar_resultados(resultado_sem, resultado_com)
    
    print("\n" + "#"*60)
    print("# FIM DO TESTE")
    print("#"*60 + "\n")