"""
Gestão de reposicionamento proativo de veículos.
"""

from typing import List
from modelo.veiculos import Veiculo
from modelo.pedidos import Pedido
from modelo.grafo import Grafo


def reposicionar_veiculo_proativo(veiculo: Veiculo, pedidos_futuros: List[Pedido], tempo_atual: int, grafo: Grafo, janela_previsao: int = 10) -> str:
    """
    Sugere zona para reposicionar veículo ocioso.
    
    Analisa pedidos esperados nos próximos N minutos
    e retorna zona de maior procura.

    Returns:
        ID da zona alvo
    """
    zonas_procura = {}
    
    for pedido in pedidos_futuros:
        # Pedidos na janela de previsão
        if tempo_atual <= pedido.instante_pedido <= tempo_atual + janela_previsao:
            zona = pedido.posicao_inicial
            zonas_procura[zona] = zonas_procura.get(zona, 0) + 1
    
    if not zonas_procura:
        return veiculo.posicao  # Fica onde está
    
    # Zona de maior procura
    zona_alvo = max(zonas_procura, key=zonas_procura.get)
    return zona_alvo