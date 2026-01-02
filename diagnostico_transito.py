#!/usr/bin/env python3
"""
Diagnóstico do sistema de trânsito dinâmico.
Executa e mostra os valores reais do congestionamento.
"""

import sys
from pathlib import Path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from testes.test_config import ConfigTestes
from gestao.transito_dinamico import GestorTransito

def diagnosticar_transito():
    """Executa diagnóstico completo do trânsito."""
    
    print("="*80)
    print("DIAGNÓSTICO DO SISTEMA DE TRÂNSITO DINÂMICO")
    print("="*80)
    print()
    
    # Cria grafo e gestor
    grafo = ConfigTestes.criar_grafo_teste()
    gestor_transito = GestorTransito(grafo)
    
    # Testa aresta Centro → Shopping
    aresta = grafo.get_aresta("Centro", "Shopping")
    tempo_base = aresta.tempoViagem_min
    
    print(f" Aresta: Centro → Shopping")
    print(f"   Tempo base: {tempo_base:.2f} min")
    print(f"   Distância: {aresta.distancia_km:.2f} km")
    print()
    
    # Testa diferentes horários
    horarios = [
        (120, "02:00", "Madrugada"),
        (420, "07:00", "Início Rush Manhã"),
        (480, "08:00", "Rush Manhã"),
        (720, "12:00", "Almoço"),
        (840, "14:00", "Tarde Normal"),
        (1020, "17:00", "Rush Tarde"),
        (1080, "18:00", "Pico Rush Tarde"),
        (1320, "22:00", "Noite"),
    ]
    
    print("-"*80)
    print(f"{'Horário':<20} {'Factor':<10} {'Congestion':<12} {'Tempo Real':<12} {'Variação':<10}")
    print("-"*80)
    
    for tempo_sim, hora_str, periodo in horarios:
        # Atualiza trânsito
        gestor_transito.atualizar_transito(tempo_simulacao=tempo_sim)
        
        # Lê valores
        factor = gestor_transito.calcular_factor_hora(gestor_transito.hora_atual)
        congestion = aresta.congestion
        tempo_real = aresta.tempo_real()
        variacao = ((tempo_real / tempo_base) - 1) * 100
        
        # Mostra
        print(f"{hora_str} ({periodo})"[:20].ljust(20), end="")
        print(f"{factor:<10.2f} {congestion:<12.2f} {tempo_real:<12.2f} {variacao:+.1f}%")
    
    print("-"*80)
    print()
    
    # Verifica lógica
    print("VERIFICAÇÕES:")
    print()
    
    # Madrugada vs Rush
    gestor_transito.atualizar_transito(tempo_simulacao=120)
    cong_madrugada = aresta.congestion
    
    gestor_transito.atualizar_transito(tempo_simulacao=480)
    cong_rush = aresta.congestion
    
    if cong_rush > cong_madrugada:
        print("✓ Rush tem mais trânsito que madrugada")
    else:
        print(f"✗ ERRO: Rush ({cong_rush:.2f}) ≤ Madrugada ({cong_madrugada:.2f})")
    
    # Rush manhã vs tarde
    gestor_transito.atualizar_transito(tempo_simulacao=1080)
    cong_rush_tarde = aresta.congestion
    
    if cong_rush_tarde > cong_rush:
        print("✓ Rush tarde tem mais trânsito que rush manhã")
    else:
        print(f"✗ AVISO: Rush tarde ({cong_rush_tarde:.2f}) ≤ Rush manhã ({cong_rush:.2f})")
    
    # Madrugada < 1.0
    gestor_transito.atualizar_transito(tempo_simulacao=120)
    if aresta.congestion < 1.0:
        print("✓ Madrugada tem congestion < 1.0")
    else:
        print(f"✗ ERRO: Madrugada congestion = {aresta.congestion:.2f} (deveria ser < 1.0)")
    
    print()
    print("="*80)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("="*80)


if __name__ == '__main__':
    diagnosticar_transito()