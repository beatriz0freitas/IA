"""
Criação de veículos de demonstração e geração automática de frotas.
"""
from typing import Optional
import random
from modelo.veiculos import VeiculoEletrico, VeiculoCombustao, EstadoVeiculo
from gestao.gestor_frota import GestorFrota


class VeiculosDemo:
    @staticmethod
    def criar_frota_demo(gestor: GestorFrota) -> GestorFrota:

        nos_disponiveis = list(gestor.grafo.nos.keys())
        if len(nos_disponiveis) < 2:
            raise ValueError("O grafo do gestor não tem nós suficientes. Crie o grafo primeiro.")
        
        # Veículo Elétrico 1 - começa no Centro
        v1 = VeiculoEletrico(
            id_veiculo="E1",
            posicao="Centro",
            autonomia_km=80,
            autonomiaMax_km=80,
            capacidade_passageiros=4,
            custo_km=0.10,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            km_sem_passageiros=0,
            indice_rota=0,
            id_pedido_atual=None,
            tempo_ocupado_ate=0,
            rota=[],
            tempo_recarregamento_min=30,
            capacidade_bateria_kWh=60,
            consumo_kWh_km=0.15
        )

        # Veículo Elétrico 2 - começa na Praça
        v2 = VeiculoEletrico(
            id_veiculo="E2",
            posicao="Praça",
            autonomia_km=80,
            autonomiaMax_km=80,
            capacidade_passageiros=4,
            custo_km=0.10,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            km_sem_passageiros=0,
            indice_rota=0,
            id_pedido_atual=None,
            tempo_ocupado_ate=0,
            rota=[],
            tempo_recarregamento_min=30,
            capacidade_bateria_kWh=60,
            consumo_kWh_km=0.15
        )

        # Veículo Combustão 1 - começa no Shopping
        v3 = VeiculoCombustao(
            id_veiculo="C1",
            posicao="Shopping",
            autonomia_km=120,
            autonomiaMax_km=120,
            capacidade_passageiros=4,
            custo_km=0.20,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            km_sem_passageiros=0,
            indice_rota=0,
            id_pedido_atual=None,
            tempo_ocupado_ate=0,
            rota=[],
            tempo_reabastecimento_min=10,
            emissao_CO2_km=0.12
        )

        # Veículo Combustão 2 - começa no Aeroporto
        v4 = VeiculoCombustao(
            id_veiculo="C2",
            posicao="Aeroporto",
            autonomia_km=120,
            autonomiaMax_km=120,
            capacidade_passageiros=4,
            custo_km=0.20,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            km_sem_passageiros=0,
            indice_rota=0,
            id_pedido_atual=None,
            tempo_ocupado_ate=0,
            rota=[],
            tempo_reabastecimento_min=10,
            emissao_CO2_km=0.12
        )

        gestor.adicionar_veiculo(v1)
        gestor.adicionar_veiculo(v2)
        gestor.adicionar_veiculo(v3)
        gestor.adicionar_veiculo(v4)

        print(f"\n Frota criada:")
        print(f"   2 veículos elétricos (E1, E2)")
        print(f"   2 veículos a combustão (C1, C2)")

        return gestor
