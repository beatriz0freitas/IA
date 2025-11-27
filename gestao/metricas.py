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
        self.km_sem_passageiros: float = 0.0
        self.tempo_total_resposta: float = 0.0
        self.pedidos_servicos: int = 0
        self.pedidos_rejeitados: int = 0
        self.tempo_total_ocupacao: float = 0.0

    def atualizar_metricas(self, custo: float, emissao: float, km: float, km_sem_passageiros: float = 0.0):
        self.custo_total += custo
        self.emissoes_totais += emissao
        self.km_totais += km
        self.km_sem_passageiros += km_sem_passageiros

    # Integração com métricas a cada movimento 
    def integracao_metricas(self, v: Veiculo, distancia: float, com_passageiros: bool = False):
        custo = v.custo_operacao(distancia)
        emissao = v.calcula_emissao(distancia)
        km_sem_pass = 0.0 if com_passageiros else distancia

        self.atualizar_metricas(custo, emissao, distancia, km_sem_pass)

    def registar_pedido(self, pedido: Pedido, tempo_resposta: int):
        if pedido.estado.name == "CONCLUIDO":
            self.pedidos_servicos += 1
            self.tempo_total_resposta += tempo_resposta
        elif pedido.estado.name == "REJEITADO":
            self.pedidos_rejeitados += 1

    def calcular_metricas(self) -> Dict[str, float]:
        total_pedidos = self.pedidos_servicos + self.pedidos_rejeitados

        return {
            "custo_total": round(self.custo_total, 2),
            "emissoes_totais": round(self.emissoes_totais, 3),
            "km_totais": round(self.km_totais, 2),
            "km_sem_passageiros": round(self.km_sem_passageiros, 2),
            "percentagem_km_sem_passageiros": (
                round((self.km_sem_passageiros / self.km_totais) * 100, 1)
                if self.km_totais > 0 else 0.0
            ),
            "pedidos_servicos": self.pedidos_servicos,
            "pedidos_rejeitados": self.pedidos_rejeitados,
            "tempo_medio_resposta": (
                round(self.tempo_total_resposta / self.pedidos_servicos, 2)
                if self.pedidos_servicos > 0 else 0.0
            ),
            "taxa_sucesso": (
                round(self.pedidos_servicos / total_pedidos * 100, 1)
                if total_pedidos > 0 else 0.0
            )
        }

