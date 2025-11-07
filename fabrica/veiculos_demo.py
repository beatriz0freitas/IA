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
        v1 = VeiculoEletrico(
            id_veiculo="E1",
            posicao="A",
            autonomia_km=20,
            autonomiaMax_km=20,
            capacidade_passageiros=4,
            custo_km=0.10,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            id_rota="R1",
            rota=[],
            tempo_recarregamento_min=8,
            capacidade_bateria_kWh=45,
            consumo_kWh_km=0.16
        )

        v2 = VeiculoCombustao(
            id_veiculo="C1",
            posicao="C",
            autonomia_km=35,
            autonomiaMax_km=35,
            capacidade_passageiros=4,
            custo_km=0.20,
            estado=EstadoVeiculo.DISPONIVEL,
            km_total=0,
            id_rota="R2",
            rota=[],
            tempo_reabastecimento_min=6,
            emissao_CO2_km=0.12
        )

        gestor.adicionar_veiculo(v1)
        gestor.adicionar_veiculo(v2)

        return gestor

    @staticmethod
    def criar_frota_mista(gestor: GestorFrota, n_eletricos: int, n_combustao: int) -> GestorFrota:

        nos = list(gestor.grafo.nos.keys())
        if not nos:
            raise ValueError("O grafo do gestor não tem nós. Crie o grafo primeiro.")

        # Elétricos
        for i in range(1, n_eletricos + 1):
            pos = random.choice(nos)
            v = VeiculoEletrico(
                id_veiculo=f"E{i}",
                posicao=pos,
                autonomia_km=random.uniform(15, 50),
                autonomiaMax_km=50,
                capacidade_passageiros=4,
                custo_km=0.1,
                estado=EstadoVeiculo.DISPONIVEL,
                km_total=0,
                id_rota=f"RE{i}",
                rota=[],
                tempo_recarregamento_min=random.randint(5, 15),
                capacidade_bateria_kWh=random.uniform(30, 70),
                consumo_kWh_km=round(random.uniform(0.12, 0.2), 2)
            )
            gestor.adicionar_veiculo(v)

        # Combustão
        for i in range(1, n_combustao + 1):
            pos = random.choice(nos)
            v = VeiculoCombustao(
                id_veiculo=f"C{i}",
                posicao=pos,
                autonomia_km=random.uniform(30, 80),
                autonomiaMax_km=80,
                capacidade_passageiros=4,
                custo_km=0.2,
                estado=EstadoVeiculo.DISPONIVEL,
                km_total=0,
                id_rota=f"RC{i}",
                rota=[],
                tempo_reabastecimento_min=random.randint(5, 12),
                emissao_CO2_km=round(random.uniform(0.1, 0.2), 3)
            )
            gestor.adicionar_veiculo(v)

        return gestor
