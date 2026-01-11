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
            "perc_km_vazio": (
                round((self.km_sem_passageiros / self.km_totais * 100), 1)
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

    @staticmethod
    def calcular_metricas_dead_mileage(veiculos: Dict[str, Veiculo]) -> Dict:
        km_total = sum(v.km_total for v in veiculos.values())
        km_sem_pass = sum(v.km_sem_passageiros for v in veiculos.values())
        perc = (km_sem_pass / km_total * 100) if km_total > 0 else 0.0

        dead_por_veiculo = {
            v.id_veiculo: round(v.km_sem_passageiros, 2)
            for v in veiculos.values()
        }

        return {
            "km_total": round(km_total, 2),
            "km_sem_passageiros": round(km_sem_pass, 2),
            "perc_dead_mileage": round(perc, 2),
            "dead_mileage_por_veiculo": dead_por_veiculo,
        }

    def calcular_metricas_extensas(self, veiculos: Dict[str, Veiculo]) -> Dict[str, object]:
        base = self.calcular_metricas()
        dead = Metricas.calcular_metricas_dead_mileage(veiculos)

        pedidos_servicos = base.get("pedidos_servicos", 0) or 0
        km_totais = base.get("km_totais", 0.0) or 0.0
        custo_total = base.get("custo_total", 0.0) or 0.0
        emissoes = base.get("emissoes_totais", 0.0) or 0.0

        custo_por_km = round(custo_total / km_totais, 3) if km_totais > 0 else 0.0
        emissao_por_km = round(emissoes / km_totais, 4) if km_totais > 0 else 0.0
        custo_por_pedido = round(custo_total / pedidos_servicos, 2) if pedidos_servicos > 0 else 0.0

        # Top veículo “dead mileage”
        dead_por_veiculo = dead["dead_mileage_por_veiculo"]
        top_dead = max(dead_por_veiculo.items(), key=lambda kv: kv[1]) if dead_por_veiculo else None

        return {
            **base,
            "custo_por_km": custo_por_km,
            "emissao_por_km": emissao_por_km,
            "custo_por_pedido_servico": custo_por_pedido,
            "dead_mileage": dead,
            "top_dead_mileage": top_dead,  # ("E1", 12.3)
        }

    @staticmethod
    def formatar_relatorio(metricas: Dict[str, object]) -> str:
        # Segurança
        def g(k, default=0):
            return metricas.get(k, default)

        linhas = []
        linhas.append("=" * 60)
        linhas.append("RESULTADOS FINAIS (TaxiGreen)")
        linhas.append("=" * 60)

        linhas.append("\nPedidos")
        linhas.append(f"  - Pedidos servidos:     {g('pedidos_servicos')}")
        linhas.append(f"  - Pedidos rejeitados:   {g('pedidos_rejeitados')}")
        linhas.append(f"  - Taxa de sucesso:      {g('taxa_sucesso')} %")
        linhas.append(f"  - Tempo médio resposta: {g('tempo_medio_resposta')} min")

        linhas.append("\nDistâncias")
        linhas.append(f"  - Km totais:            {g('km_totais')} km")
        linhas.append(f"  - Km sem passageiros:   {g('km_sem_passageiros')} km")
        linhas.append(f"  - % km vazio:           {g('perc_km_vazio')} %")

        linhas.append("\nCustos & Emissões")
        linhas.append(f"  - Custo total:          € {g('custo_total')}")
        linhas.append(f"  - Custo por km:         € {g('custo_por_km')}/km")
        linhas.append(f"  - Custo por pedido:     € {g('custo_por_pedido_servico')}/pedido")
        linhas.append(f"  - Emissões totais:      {g('emissoes_totais')} kgCO₂")
        linhas.append(f"  - Emissões por km:      {g('emissao_por_km')} kgCO₂/km")

        dead = metricas.get("dead_mileage", {})
        if dead:
            linhas.append("\nDead mileage (detalhe)")
            linhas.append(f"  - Total:               {dead.get('km_sem_passageiros')} km ({dead.get('perc_dead_mileage')}%)")
            top_dead = metricas.get("top_dead_mileage")
            if top_dead:
                linhas.append(f"  - Pior veículo (vazio): {top_dead[0]} com {top_dead[1]} km")

        linhas.append("\n" + "=" * 60)
        return "\n".join(linhas)
