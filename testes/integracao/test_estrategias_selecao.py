"""
Testes de Integração - Gestor de Frota
"""

import unittest
from testes.test_config import ConfigTestes
from modelo.pedidos import Pedido, EstadoPedido
from gestao.estrategia_selecao import (SelecaoMenorDistancia, SelecaoCustoComposto, SelecaoDeadMileage, SelecaoEquilibrada)
from gestao.funcao_custo import FuncaoCustoComposta

class TestEstrategiasSelecao(unittest.TestCase):
    
    def setUp(self):
        from gestao.estrategia_selecao import (
            SelecaoMenorDistancia, SelecaoCustoComposto, 
            SelecaoDeadMileage, SelecaoEquilibrada
        )
        from gestao.funcao_custo import FuncaoCustoComposta
        
        self.gestor = ConfigTestes.criar_gestor_teste()
        
        self.estrategia_distancia = SelecaoMenorDistancia()
        self.estrategia_custo = SelecaoCustoComposto(FuncaoCustoComposta())
        self.estrategia_dead = SelecaoDeadMileage(penalizacao=2.0)
        self.estrategia_equilibrada = SelecaoEquilibrada()
        
        self.pedido = Pedido(
            id_pedido="P_TESTE",
            posicao_inicial="Centro",
            posicao_destino="Aeroporto",
            passageiros=2,
            instante_pedido=10,
            prioridade=2,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            tempo_max_espera=30
        )
    
    def test_selecao_menor_distancia(self):
        """Testa estratégia de menor distância."""
        candidatos = self.gestor.veiculos_disponiveis()
        
        veiculo = self.estrategia_distancia.selecionar(
            self.pedido, candidatos, self.gestor, tempo_atual=10
        )
        
        self.assertIsNotNone(veiculo)
    
    def test_selecao_custo_composto(self):
        """Testa estratégia de custo composto."""
        candidatos = self.gestor.veiculos_disponiveis()
        
        veiculo = self.estrategia_custo.selecionar(
            self.pedido, candidatos, self.gestor, tempo_atual=10
        )
        
        self.assertIsNotNone(veiculo)
    
    def test_selecao_dead_mileage_penaliza_distantes(self):
        """Testa que dead mileage penaliza veículos distantes."""
        candidatos = self.gestor.veiculos_disponiveis()
        
        # Coloca veículos em posições diferentes
        candidatos[0].posicao = "Centro"  # Próximo
        candidatos[1].posicao = "Porto"   # Distante
        
        veiculo = self.estrategia_dead.selecionar(
            self.pedido, candidatos[:2], self.gestor, tempo_atual=10
        )
        
        # Deve escolher o mais próximo
        self.assertEqual(veiculo.posicao, "Centro")
    
    def test_trocar_estrategia_dinamicamente(self):
        """Testa mudança dinâmica de estratégia."""
        self.gestor.definir_estrategia_selecao(self.estrategia_distancia)
        
        veiculo1 = self.gestor.selecionar_veiculo_pedido(
            self.pedido, tempo_atual=10
        )
        
        self.gestor.definir_estrategia_selecao(self.estrategia_custo)
        
        veiculo2 = self.gestor.selecionar_veiculo_pedido(
            self.pedido, tempo_atual=10
        )
        
        # Ambas devem retornar veículo (podem ser diferentes)
        self.assertIsNotNone(veiculo1)
        self.assertIsNotNone(veiculo2)

if __name__ == '__main__':
    unittest.main()