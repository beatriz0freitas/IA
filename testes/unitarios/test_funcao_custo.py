"""
Testes Unitários - Função de Custo Composta
"""

import unittest
from modelo.veiculos import VeiculoEletrico, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from gestao.funcao_custo import FuncaoCustoComposta, PesosCusto

from testes.test_config import ConfigTestes

class TestFuncaoCusto(unittest.TestCase):
    
    def setUp(self):
        """Setup comum."""
        from gestao.funcao_custo import FuncaoCustoComposta, PesosCusto
        from modelo.veiculos import VeiculoEletrico, EstadoVeiculo
        from modelo.pedidos import Pedido, EstadoPedido
        
        self.funcao_custo = FuncaoCustoComposta()
        
        self.veiculo = VeiculoEletrico(
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
        
        self.pedido = Pedido(
            id_pedido="P1",
            posicao_inicial="Centro",
            posicao_destino="Shopping",
            passageiros=2,
            instante_pedido=10,
            prioridade=2,
            pref_ambiental="eletrico",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )
    
    def test_custo_atribuicao(self):
        """Testa cálculo de custo composto."""
        custo = self.funcao_custo.calcular_custo_atribuicao(
            self.veiculo, self.pedido, 
            tempo_resposta=5.0, 
            distancia_total=10.0
        )
        
        self.assertGreater(custo, 0.0)
        self.assertIsInstance(custo, float)
    
    def test_prioridade_alta_penaliza_demora(self):
        """Testa que alta prioridade + demora = penalização."""
        pedido_urgente = self.pedido
        pedido_urgente.prioridade = 3
        
        custo_rapido = self.funcao_custo.calcular_custo_atribuicao(
            self.veiculo, pedido_urgente, 
            tempo_resposta=5.0, 
            distancia_total=10.0
        )
        
        custo_lento = self.funcao_custo.calcular_custo_atribuicao(
            self.veiculo, pedido_urgente, 
            tempo_resposta=15.0,  # Demora
            distancia_total=10.0
        )
        
        self.assertGreater(custo_lento, custo_rapido)
    
    def test_pesos_personalizados(self):
        """Testa criação com pesos personalizados."""
        from gestao.funcao_custo import PesosCusto
        
        pesos = PesosCusto(
            tempo=0.5,
            custo=0.2,
            emissao=0.2,
            rejeicao=0.1
        )
        
        funcao = FuncaoCustoComposta(pesos)
        self.assertEqual(funcao.pesos.tempo, 0.5)

if __name__ == '__main__':
    unittest.main()