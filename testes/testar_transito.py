"""
Script para testar o sistema de trânsito dinâmico.
"""

from fabrica.grafo_demo import GrafoDemo
from gestao.transito_dinamico import GestorTransito


def main():
    print("\n🚦 TESTE DO SISTEMA DE TRÂNSITO DINÂMICO\n")

    # Cria grafo
    grafo = GrafoDemo.criar_grafo_demo()

    # Cria gestor de trânsito
    gestor = GestorTransito(grafo)

    # Testa diferentes horas do dia
    horas_teste = [
        (0, "00:00 - Madrugada"),
        (480, "08:00 - Rush manhã"),
        (600, "10:00 - Final rush manhã"),
        (720, "12:00 - Hora almoço"),
        (1080, "18:00 - Rush tarde"),
        (1320, "22:00 - Noite"),
    ]

    print("="*80)
    print("VARIAÇÃO DE TRÂNSITO POR HORA DO DIA")
    print("="*80)

    for minutos, descricao in horas_teste:
        gestor.atualizar_transito(minutos)
        estado = gestor.obter_estado_transito()

        print(f"\n{descricao}")
        print(f"  Hora: {estado['hora_atual']:02d}:00")
        print(f"  Factor base: {estado['factor_base']:.1f}x")
        print(f"  Congestionamento médio: {estado['congestion_media']:.2f}x")

    # Testa aresta específica (Centro → Shopping)
    print("\n" + "="*80)
    print("COMPARAÇÃO: CENTRO → SHOPPING em diferentes horas")
    print("="*80)

    aresta = grafo.get_aresta("Centro", "Shopping")
    tempo_base = aresta.tempoViagem_min

    for minutos, descricao in horas_teste:
        gestor.atualizar_transito(minutos)
        aresta_atualizada = grafo.get_aresta("Centro", "Shopping")

        print(f"\n{descricao}")
        print(f"  Tempo base: {tempo_base:.1f} min")
        print(f"  Congestionamento: {aresta_atualizada.congestion:.2f}x")
        print(f"  Tempo real: {aresta_atualizada.tempo_real():.1f} min")
        print(f"  Diferença: +{aresta_atualizada.tempo_real() - tempo_base:.1f} min")

    # Testa bloqueio de estrada
    print("\n" + "="*80)
    print("TESTE DE BLOQUEIO DE ESTRADA")
    print("="*80)

    gestor.simular_bloqueio("Centro", "Shopping", bloquear=True)
    aresta_bloqueada = grafo.get_aresta("Centro", "Shopping")

    print(f"\nEstrada Centro → Shopping bloqueada")
    print(f"  Blocked: {aresta_bloqueada.blocked}")
    print(f"  Tempo real: {aresta_bloqueada.tempo_real()}")

    # Desbloqueia
    gestor.simular_bloqueio("Centro", "Shopping", bloquear=False)
    aresta_desbloqueada = grafo.get_aresta("Centro", "Shopping")

    print(f"\nEstrada Centro → Shopping desbloqueada")
    print(f"  Blocked: {aresta_desbloqueada.blocked}")
    print(f"  Tempo real: {aresta_desbloqueada.tempo_real():.1f} min")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
