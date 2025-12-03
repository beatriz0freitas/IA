"""
Script para testar o sistema de falhas em estações.
"""

from fabrica.grafo_demo import GrafoDemo
from gestao.gestor_falhas import GestorFalhas


def main():
    print("\n⚡ TESTE DO SISTEMA DE FALHAS EM ESTAÇÕES\n")

    # Cria grafo
    grafo = GrafoDemo.criar_grafo_demo()

    # Cria gestor de falhas (com probabilidade alta para testes)
    gestor = GestorFalhas(grafo, prob_falha=0.2)

    print("="*80)
    print("ESTADO INICIAL")
    print("="*80)

    estado = gestor.obter_estado_estacoes()
    print(f"\nEstações de Recarga:")
    print(f"  Total: {estado['estacoes_recarga']['total']}")
    print(f"  Online: {estado['estacoes_recarga']['online']}")
    print(f"  Offline: {estado['estacoes_recarga']['offline']}")
    print(f"  Disponibilidade: {estado['estacoes_recarga']['taxa_disponibilidade']}%")

    print(f"\nPostos de Abastecimento:")
    print(f"  Total: {estado['postos_abastecimento']['total']}")
    print(f"  Online: {estado['postos_abastecimento']['online']}")
    print(f"  Offline: {estado['postos_abastecimento']['offline']}")
    print(f"  Disponibilidade: {estado['postos_abastecimento']['taxa_disponibilidade']}%")

    # Simula falhas ao longo do tempo
    print("\n" + "="*80)
    print("SIMULAÇÃO DE FALHAS (10 iterações)")
    print("="*80)

    for t in range(10):
        falhas = gestor.simular_falha_aleatoria(t)

        if falhas:
            print(f"\n[t={t}] ⚠️ Falhas detectadas:")
            for est in falhas:
                print(f"  - {est} OFFLINE")

        estado = gestor.obter_estado_estacoes()
        print(f"[t={t}] Recarga: {estado['estacoes_recarga']['online']}/{estado['estacoes_recarga']['total']} | "
              f"Postos: {estado['postos_abastecimento']['online']}/{estado['postos_abastecimento']['total']}")

    # Teste de falha forçada
    print("\n" + "="*80)
    print("TESTE DE FALHA FORÇADA")
    print("="*80)

    print("\nForçar falha na 'Recarga_Centro'...")
    sucesso = gestor.forcar_falha("Recarga_Centro", 10)
    print(f"Sucesso: {sucesso}")

    no = grafo.nos["Recarga_Centro"]
    print(f"Estado da estação: {'OFFLINE' if not no.disponivel else 'ONLINE'}")

    # Recuperação manual
    print("\nRecuperar 'Recarga_Centro'...")
    sucesso = gestor.recuperar_estacao("Recarga_Centro", 11)
    print(f"Sucesso: {sucesso}")

    no = grafo.nos["Recarga_Centro"]
    print(f"Estado da estação: {'OFFLINE' if not no.disponivel else 'ONLINE'}")

    # Histórico
    print("\n" + "="*80)
    print("HISTÓRICO DE EVENTOS")
    print("="*80)

    print(f"\nTotal de eventos: {len(gestor.historico_falhas)}")
    print("\nÚltimos 10 eventos:")
    for evento in gestor.historico_falhas[-10:]:
        print(f"  [t={evento['tempo']}] {evento['estacao']}: {evento['tipo']}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
