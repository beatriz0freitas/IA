from __future__ import annotations
from typing import Dict, List
from modelo.veiculos import Veiculo
from modelo.pedidos import Pedido

"""
Recolhe e calcula métricas globais da frota após uma simulação.
Pode ser alimentada diretamente pelo GestorFrota ou pós-processamento.
"""
class Metricas:

    def __init__(self):
        self.custo_total: float = 0.0
        self.emissoes_totais: float = 0.0
        self.km_totais: float = 0.0
        self.tempo_total_resposta: float = 0.0
        self.pedidos_servicos: int = 0
        self.pedidos_rejeitados: int = 0

    def atualizar_metricas(self, custo: float, emissao: float, km: float):
        self.custo_total += custo
        self.emissoes_totais += emissao
        self.km_totais += km

    # Integração com métricas a cada movimento 
    def integracao_metricas(self, v: Veiculo, distancia: float):
        custo = v.custo_operacao(distancia)
        emissao = v.calcula_emissao(distancia)
        self.atualizar_metricas(custo, emissao, distancia)

    def registar_evento(self, tempo: int, pedido: Pedido, veiculo_id: str):
        self.eventos.append({
            "tempo": tempo,
            "pedido": pedido.id_pedido,
            "veiculo": veiculo_id,
            "estado": pedido.estado
        })

    def registar_pedido(self, pedido: Pedido, tempo_resposta: int):
        if pedido.estado.name == "CONCLUIDO":
            self.pedidos_servicos += 1
            self.tempo_total_resposta += tempo_resposta
        elif pedido.estado.name == "REJEITADO":
            self.pedidos_rejeitados += 1

    def calcular_metricas(self) -> Dict[str, float]:
        return {
            "custo_total": round(self.custo_total, 2),
            "emissoes_totais": round(self.emissoes_totais, 3),
            "km_totais": round(self.km_totais, 2),
            "pedidos_servicos": self.pedidos_servicos,
            "pedidos_rejeitados": self.pedidos_rejeitados,
            "tempo_medio_resposta": (
                round(self.tempo_total_resposta / self.pedidos_servicos, 2)
                if self.pedidos_servicos > 0 else 0.0
            ),
            "taxa_sucesso": (
                round(self.pedidos_servicos /
                      (self.pedidos_servicos + self.pedidos_rejeitados), 2)
                if (self.pedidos_servicos + self.pedidos_rejeitados) > 0 else 0.0
            )
        }

