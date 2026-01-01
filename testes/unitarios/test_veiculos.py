"""
Testes Unitários - Veículos
"""

import unittest
from modelo.veiculos import VeiculoEletrico, VeiculoCombustao, EstadoVeiculo
from testes.test_config import ConfigTestes


class TestVeiculos(unittest.TestCase):
    
    def setUp(self):
        """Setup de veículos de teste."""
        from modelo.veiculos import VeiculoEletrico, VeiculoCombustao, EstadoVeiculo
        
        self.veiculo_eletrico = VeiculoEletrico(
            id_veiculo="E1",
            posicao="Centro",
            autonomia_km=50.0,
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
    
    def test_tipo_veiculo(self):
        """Testa identificação correta do tipo."""
        self.assertEqual(self.veiculo_eletrico.tipo_veiculo(), "eletrico")
        self.assertEqual(self.veiculo_combustao.tipo_veiculo(), "combustao")
    
    def test_consegue_percorrer(self):
        """Testa verificação de autonomia."""
        self.assertTrue(self.veiculo_eletrico.consegue_percorrer(30.0))
        self.assertFalse(self.veiculo_eletrico.consegue_percorrer(60.0))
    
    def test_pode_transportar(self):
        """Testa capacidade de passageiros."""
        self.assertTrue(self.veiculo_eletrico.pode_transportar(4))
        self.assertFalse(self.veiculo_eletrico.pode_transportar(5))
    
    def test_emissao_eletrico(self):
        """Testa que veículo elétrico não emite CO2."""
        emissao = self.veiculo_eletrico.calcula_emissao(10.0)
        self.assertEqual(emissao, 0.0)
    
    def test_emissao_combustao(self):
        """Testa cálculo de emissões."""
        emissao = self.veiculo_combustao.calcula_emissao(10.0)
        expected = 10.0 * 0.12
        self.assertAlmostEqual(emissao, expected, places=3)
    
    def test_custo_operacao_eletrico_menor(self):
        """Testa que elétrico é mais barato."""
        custo_eletrico = self.veiculo_eletrico.custo_operacao(10.0)
        custo_combustao = self.veiculo_combustao.custo_operacao(10.0)
        
        self.assertLess(custo_eletrico, custo_combustao)
    
    def test_move_atualiza_autonomia(self):
        """Testa que movimento consome autonomia."""
        autonomia_inicial = self.veiculo_eletrico.autonomia_km
        self.veiculo_eletrico.move(10.0, "NovoNo", com_passageiros=True)
        
        self.assertLess(self.veiculo_eletrico.autonomia_km, autonomia_inicial)
        self.assertEqual(self.veiculo_eletrico.posicao, "NovoNo")
    
    def test_km_sem_passageiros(self):
        """Testa contabilização de km vazio."""
        self.veiculo_eletrico.move(10.0, "A", com_passageiros=False)
        self.assertEqual(self.veiculo_eletrico.km_sem_passageiros, 10.0)
        
        self.veiculo_eletrico.move(5.0, "B", com_passageiros=True)
        self.assertEqual(self.veiculo_eletrico.km_sem_passageiros, 10.0)

if __name__ == '__main__':
    unittest.main()