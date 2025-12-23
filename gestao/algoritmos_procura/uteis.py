"""
Funções auxiliares comuns a vários algoritmos:
- Cálculo de distância euclidiana
- Funções de custo ou tempo estimado
- Outras heurísticas futuras
"""

import math
from modelo.grafo import No

# Calcula a distância euclidiana (em km) entre dois nós.
def dist_euclidiana(no_a: No, no_b: No) -> float:
    return math.hypot(no_a.posicaox - no_b.posicaox, no_a.posicaoy - no_b.posicaoy)


# Estima o tempo (em minutos) entre dois nós com base na distância euclidiana.
def tempo_heuristica(no_a: No, no_b: No,
                     velocidadeMedia_kmh: float = 40.0) -> float:
    dist_km = dist_euclidiana(no_a, no_b)
    if velocidadeMedia_kmh <= 0:
        velocidadeMedia_kmh = 40.0
    return (dist_km / velocidadeMedia_kmh) * 60.0  # minutos


def heuristica_avancada(grafo, veiculo, no_atual, no_destino, tempo_atual):
    """
    Heurística admissível que considera múltiplos fatores
    """
    dist_euclidiana = dist_euclidiana(no_atual, no_destino)
    
    # Tempo estimado (velocidade máxima possível = otimista = admissível)
    velocidade_maxima = 50  # km/h (velocidade de autoestrada)
    tempo_base = (dist_euclidiana / velocidade_maxima) * 60  # minutos
    
    # Penalização por autonomia insuficiente (se aplicável)
    penalizacao_autonomia = 0
    if veiculo.autonomia_km < dist_euclidiana:
        # Vai precisar de recarga - estima tempo mínimo de recarga
        autonomia_faltante = dist_euclidiana - veiculo.autonomia_km
        if veiculo.tipo_veiculo() == "eletrico":
            # Tempo mínimo de recarga (otimista)
            penalizacao_autonomia = 15  # 15 min mínimo
        else:
            penalizacao_autonomia = 5   # 5 min mínimo (abastecimento)
    
    # Factor de trânsito esperado (média histórica - otimista)
    hora_atual = (tempo_atual // 60) % 24
    if 7 <= hora_atual <= 9 or 17 <= hora_atual <= 19:
        factor_transito = 1.2  # Rush hour (otimista, pior caso seria 2.0)
    else:
        factor_transito = 1.0
    
    return tempo_base * factor_transito + penalizacao_autonomia