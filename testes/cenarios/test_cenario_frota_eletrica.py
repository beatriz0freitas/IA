"""
Testes de Cenários - 100% Frota Elétrica
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes
from modelo.veiculos import VeiculoEletrico, EstadoVeiculo
from gestao.gestor_frota import GestorFrota
from modelo.grafo import Grafo

class TestCenarioFrotaEletrica(unittest.TestCase):
    
    def setUp(self):
        from modelo.veiculos import VeiculoEletrico, EstadoVeiculo
        from modelo.grafo import Grafo
        from gestao.gestor_frota import GestorFrota
        
        grafo = ConfigTestes.criar_grafo_teste()
        self.gestor = GestorFrota(grafo)
        
        # Adiciona apenas elétricos
        for i in range(4):
            veiculo = VeiculoEletrico(
                id_veiculo=f"E{i+1}",
                posicao="Centro",
                autonomia_km=60.0,
                autonomiaMax_km=80.0,
                capacidade_passageiros=4,
                custo_km=0.10,
                estado=EstadoVeiculo.DISPONIVEL,
                km_total=0.0,
                km_sem_passageiros=0.0,
                indice_rota=0,
                tempo_recarregamento_min=30,
                capacidade_bateria_kWh=60,
                consumo_kWh_km=0.15
            )
            self.gestor.adicionar_veiculo(veiculo)
        
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_emissoes_zero(self):
        """Frota 100% elétrica deve ter emissões zero."""
        # Cria pedidos
        for i in range(5):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 3,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        self.assertEqual(metricas['emissoes_totais'], 0.0)

if __name__ == '__main__':
    unittest.main()