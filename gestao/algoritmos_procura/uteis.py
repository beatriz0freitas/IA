"""
Funções auxiliares comuns a vários algoritmos:
- Cálculo de distância euclidiana
- Funções de custo ou tempo estimado
- Outras heurísticas futuras
"""

import math
from modelo.grafo import No
from modelo.grafo import Grafo

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



def heuristica_avancada(grafo: Grafo, veiculo, no_atual_id: str, no_destino_id: str, tempo_atual: int) -> float:
    """
    Heurística admissível que considera:
    - Distância euclidiana (sempre admissível)
    - Autonomia insuficiente (penalização)
    - Trânsito esperado (factor otimista)
    """
    no_atual = grafo.nos[no_atual_id]
    no_destino = grafo.nos[no_destino_id]
    
    # Distância euclidiana base (sempre admissível)
    dist_euclidiana = dist_euclidiana(no_atual, no_destino)
    
    # Tempo estimado com velocidade MÁXIMA (otimista = admissível)
    velocidade_maxima = 50.0  # km/h (autoestrada)
    tempo_base = (dist_euclidiana / velocidade_maxima) * 60  # minutos
    
    # Penalização por autonomia insuficiente
    penalizacao_autonomia = 0.0
    if veiculo and veiculo.autonomia_km < dist_euclidiana:
        # Vai precisar de recarga/abastecimento
        autonomia_faltante = dist_euclidiana - veiculo.autonomia_km
        
        if veiculo.tipo_veiculo() == "eletrico":
            # Tempo MÍNIMO de recarga (otimista) - Assumimos recarga parcial mínima (20%)
            tempo_min_recarga = 30 * 0.2  # 6 minutos
            penalizacao_autonomia = tempo_min_recarga
        else:
            # Tempo MÍNIMO de abastecimento (otimista)
            tempo_min_abastecimento = 10 * 0.2  # 2 minutos
            penalizacao_autonomia = tempo_min_abastecimento
    
    # Factor de trânsito esperado (OTIMISTA = admissível)
    hora_atual = (tempo_atual // 60) % 24
    if 7 <= hora_atual <= 9 or 17 <= hora_atual <= 19:
        # Rush hour: usa factor MÍNIMO esperado (otimista)
        factor_transito = 1.2  # Real pode ser até 2.0
    else:
        factor_transito = 1.0
    
    custo_estimado = tempo_base * factor_transito + penalizacao_autonomia
    
    return custo_estimado