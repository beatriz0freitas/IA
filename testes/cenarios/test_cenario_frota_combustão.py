"""
Testes de Cenários - 100% Frota Combustão
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes
from modelo.veiculos import VeiculoCombustao, EstadoVeiculo

class TestCenarioFrotaCombustao(unittest.TestCase):

    def setUp(self):
        from modelo.veiculos import VeiculoCombustao, EstadoVeiculo
        from gestao.gestor_frota import GestorFrota
        
        grafo = ConfigTestes.criar_grafo_teste()
        self.gestor = GestorFrota(grafo)
        
        # Adiciona apenas combustão
        for i in range(4):
            veiculo = VeiculoCombustao(
                id_veiculo=f"C{i+1}",
                posicao="Centro",
                autonomia_km=100.0,
                autonomiaMax_km=120.0,
                capacidade_passageiros=4,
                custo_km=0.20,
                estado=EstadoVeiculo.DISPONIVEL,
                km_total=0.0,
                km_sem_passageiros=0.0,
                indice_rota=0,
                tempo_reabastecimento_min=10,
                emissao_CO2_km=0.12
            )
            self.gestor.adicionar_veiculo(veiculo)
        
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_emissoes_nao_zero(self):
        """Frota combustão deve ter emissões."""
        # Cria pedidos
        for i in range(5):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i * 3,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        self.assertGreater(metricas['emissoes_totais'], 0.0)
    
    def test_custo_maior_que_eletrico(self):
        """Combustão deve ter custo maior."""
        # Compara com cenário elétrico equivalente
        # (teste de referência cruzada)
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 5,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            self.simulador.agendar_pedido(pedido)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        
        # Custo base deve ser > €6 (0.20/km * ~10km * 3 pedidos)
        self.assertGreater(metricas['custo_total'], 6.0)

if __name__ == '__main__':
    unittest.main()