"""
Sistema de otimização de rotas para minimizar km sem passageiros.
"""

from typing import List, Tuple, Dict
from modelo.pedidos import Pedido
from modelo.veiculos import Veiculo
from modelo.grafo import Grafo
import math


def calcular_distancia_euclidiana(grafo: Grafo, no1_id: str, no2_id: str) -> float:
    """Calcula distância euclidiana entre dois nós"""
    no1 = grafo.nos[no1_id]
    no2 = grafo.nos[no2_id]
    return math.hypot(no1.posicaox - no2.posicaox, no1.posicaoy - no2.posicaoy)


def agrupar_pedidos_proximos(pedidos: List[Pedido], grafo: Grafo, raio_km: float = 5.0) -> List[List[Pedido]]:
    """
    Agrupa pedidos geograficamente próximos.
    
    Returns:
        Lista de clusters (cada cluster é uma lista de pedidos)
    """
    if not pedidos:
        return []
    
    clusters = []
    visitados = set()
    
    for p1 in pedidos:
        if p1.id_pedido in visitados:
            continue
        
        cluster = [p1]
        visitados.add(p1.id_pedido)
        
        for p2 in pedidos:
            if p2.id_pedido in visitados:
                continue
            
            # Verifica proximidade de ORIGEM
            dist_origem = calcular_distancia_euclidiana(grafo, p1.posicao_inicial, p2.posicao_inicial)
            
            # Verifica proximidade de DESTINO
            dist_destino = calcular_distancia_euclidiana(grafo, p1.posicao_destino, p2.posicao_destino)
            
            # Agrupa se ambos (origem E destino) estão próximos
            if dist_origem <= raio_km and dist_destino <= raio_km:
                cluster.append(p2)
                visitados.add(p2.id_pedido)
        
        clusters.append(cluster)
    
    return clusters


def selecionar_veiculo_minimizar_dead_mileage(pedido: Pedido, veiculos_disponiveis: List[Veiculo], gestor_frota, penalizacao_dead_mileage: float = 2.0) -> Tuple[Veiculo, float]:
    """
    Seleciona veículo minimizando km sem passageiros (dead mileage).
        - penalizacao_dead_mileage: Penalização aplicada a km sem passageiros (default: 2x)
    
    Returns:
        (veiculo_escolhido, custo_total)
    """
    melhor_veiculo = None
    menor_custo_total = float('inf')
    
    for veiculo in veiculos_disponiveis:
        # Distância até pickup (DEAD MILEAGE)
        caminho_pickup, _ = gestor_frota.calcular_rota(
            veiculo.posicao, pedido.posicao_inicial, veiculo=veiculo
        )
        dist_pickup = gestor_frota.calcular_distancia_rota(caminho_pickup)
        
        if dist_pickup == float('inf'):
            continue
        
        # Distância da viagem com passageiro (ÚTIL)
        caminho_viagem, _ = gestor_frota.calcular_rota(
            pedido.posicao_inicial, pedido.posicao_destino, veiculo=veiculo
        )
        dist_viagem = gestor_frota.calcular_distancia_rota(caminho_viagem)
        
        if dist_viagem == float('inf') or not veiculo.consegue_percorrer(dist_pickup + dist_viagem):
            continue
        
        # Custo ponderado: PENALIZA dead mileage
        custo_dead = dist_pickup * penalizacao_dead_mileage  # 2x penalização
        custo_util = dist_viagem * 1.0                        # Normal
        custo_total = custo_dead + custo_util
        
        if custo_total < menor_custo_total:
            menor_custo_total = custo_total
            melhor_veiculo = veiculo
    
    return melhor_veiculo, menor_custo_total


def reposicionar_veiculo_proativo(veiculo: Veiculo, pedidos_futuros: List[Pedido], tempo_atual: int, grafo: Grafo, janela_previsao: int = 10) -> str:
    """
    Sugere zona para reposicionar veículo.
    
    Analisa pedidos que vão chegar nos próximos N minutos
    e move veículo para zona de maior demanda esperada.
    
    Returns:
        ID da zona alvo para reposicionamento
    """
    # Conta demanda por zona nos próximos N minutos
    zonas_procura = {}
    
    for p in pedidos_futuros:
        # Pedidos que vão chegar em breve
        if tempo_atual <= p.instante_pedido <= tempo_atual + janela_previsao:
            zona = p.posicao_inicial
            zonas_procura[zona] = zonas_procura.get(zona, 0) + 1
    
    if not zonas_procura:
        # Sem demanda esperada, fica onde está
        return veiculo.posicao
    
    # Escolhe zona de MAIOR demanda
    zona_alvo = max(zonas_procura, key=zonas_procura.get)
    
    return zona_alvo


def calcular_metricas_dead_mileage(veiculos: Dict[str, Veiculo]) -> Dict[str, float]:
    """
    Calcula métricas detalhadas sobre km sem passageiros.
        - dead_mileage_por_veiculo: Dict {veiculo_id: km_vazio}
    """
    km_total = sum(v.km_total for v in veiculos.values())
    km_sem_pass = sum(v.km_sem_passageiros for v in veiculos.values())
    
    perc = (km_sem_pass / km_total * 100) if km_total > 0 else 0.0
    
    dead_por_veiculo = {
        v.id_veiculo: v.km_sem_passageiros 
        for v in veiculos.values()
    }
    
    return {
        "km_total": km_total,
        "km_sem_passageiros": km_sem_pass,
        "perc_dead_mileage": round(perc, 2),
        "dead_mileage_por_veiculo": dead_por_veiculo
    }