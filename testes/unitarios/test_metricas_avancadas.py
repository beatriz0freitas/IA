"""
Testes Unitários - Métricas Avançadas
"""

import unittest
from gestao.metricas import Metricas
from modelo.veiculos import VeiculoEletrico, VeiculoCombustao, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestMetricasAvancadas(unittest.TestCase):
    """Testa cálculos avançados de métricas."""
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        self.metricas = Metricas()
        
        # Cria veículos de teste
        self.veiculo_eletrico = VeiculoEletrico(
            id_veiculo="E1",
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
        
        self.veiculo_combustao = VeiculoCombustao(
            id_veiculo="C1",
            posicao="Shopping",
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
    
    def test_dead_mileage_calculation(self):
        """Testa cálculo de dead mileage."""
        # Simula movimento sem passageiros
        self.metricas.integracao_metricas(self.veiculo_eletrico, 10.0, com_passageiros=False)
        
        # Simula movimento com passageiros
        self.metricas.integracao_metricas(self.veiculo_eletrico, 15.0, com_passageiros=True)
        
        resultado = self.metricas.calcular_metricas()
        
        self.assertEqual(resultado['km_sem_passageiros'], 10.0)
        self.assertEqual(resultado['km_totais'], 25.0)
        self.assertEqual(resultado['perc_km_vazio'], 40.0)
    
    def test_emissoes_zero_eletrico(self):
        """Testa que veículo elétrico não emite CO2."""
        self.metricas.integracao_metricas(self.veiculo_eletrico, 50.0, com_passageiros=True)
        
        resultado = self.metricas.calcular_metricas()
        self.assertEqual(resultado['emissoes_totais'], 0.0)
    
    def test_emissoes_combustao(self):
        """Testa cálculo de emissões de combustão."""
        # 50 km * 0.12 kg/km = 6.0 kg CO2
        self.metricas.integracao_metricas(self.veiculo_combustao, 50.0, com_passageiros=True)
        
        resultado = self.metricas.calcular_metricas()
        self.assertAlmostEqual(resultado['emissoes_totais'], 6.0, places=2)
    
    def test_custo_operacional_eletrico_menor(self):
        """Testa que elétrico é mais barato."""
        distancia = 20.0
        
        metricas_e = Metricas()
        metricas_c = Metricas()
        
        metricas_e.integracao_metricas(self.veiculo_eletrico, distancia, True)
        metricas_c.integracao_metricas(self.veiculo_combustao, distancia, True)
        
        custo_e = metricas_e.calcular_metricas()['custo_total']
        custo_c = metricas_c.calcular_metricas()['custo_total']
        
        self.assertLess(custo_e, custo_c)
    
    def test_tempo_medio_resposta(self):
        """Testa cálculo de tempo médio de resposta."""
        pedido1 = Pedido(
            id_pedido="P1",
            posicao_inicial="A",
            posicao_destino="B",
            passageiros=1,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.CONCLUIDO,
            veiculo_atribuido="E1"
        )
        
        pedido2 = Pedido(
            id_pedido="P2",
            posicao_inicial="C",
            posicao_destino="D",
            passageiros=1,
            instante_pedido=5,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.CONCLUIDO,
            veiculo_atribuido="E1"
        )
        
        # Tempos de resposta: 10 e 20 minutos
        self.metricas.registar_pedido(pedido1, tempo_resposta=10)
        self.metricas.registar_pedido(pedido2, tempo_resposta=20)
        
        resultado = self.metricas.calcular_metricas()
        self.assertEqual(resultado['tempo_medio_resposta'], 15.0)
    
    def test_taxa_sucesso(self):
        """Testa cálculo de taxa de sucesso."""
        pedido_ok = Pedido(
            id_pedido="P1",
            posicao_inicial="A",
            posicao_destino="B",
            passageiros=1,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.CONCLUIDO,
            veiculo_atribuido="E1"
        )
        
        pedido_rejeitado = Pedido(
            id_pedido="P2",
            posicao_inicial="C",
            posicao_destino="D",
            passageiros=1,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.REJEITADO,
            veiculo_atribuido=None
        )
        
        self.metricas.registar_pedido(pedido_ok, 5)
        self.metricas.registar_pedido(pedido_rejeitado, 0)
        
        resultado = self.metricas.calcular_metricas()
        
        # 1 sucesso de 2 = 50%
        self.assertEqual(resultado['taxa_sucesso'], 50.0)
        self.assertEqual(resultado['pedidos_servicos'], 1)
        self.assertEqual(resultado['pedidos_rejeitados'], 1)
    
    def test_metricas_dead_mileage_por_veiculo(self):
        """Testa métricas de dead mileage por veículo."""
        veiculos = {
            "E1": self.veiculo_eletrico,
            "C1": self.veiculo_combustao
        }
        
        # Simula movimentos
        self.veiculo_eletrico.move(10.0, "A", com_passageiros=False)
        self.veiculo_eletrico.move(5.0, "B", com_passageiros=True)
        
        self.veiculo_combustao.move(8.0, "C", com_passageiros=False)
        self.veiculo_combustao.move(12.0, "D", com_passageiros=True)
        
        resultado = Metricas.calcular_metricas_dead_mileage(veiculos)
        
        self.assertEqual(resultado['km_sem_passageiros'], 18.0)  # 10 + 8
        self.assertEqual(resultado['km_total'], 35.0)  # 10+5+8+12
        
        # Verifica por veículo
        self.assertEqual(resultado['dead_mileage_por_veiculo']['E1'], 10.0)
        self.assertEqual(resultado['dead_mileage_por_veiculo']['C1'], 8.0)


if __name__ == '__main__':
    unittest.main()