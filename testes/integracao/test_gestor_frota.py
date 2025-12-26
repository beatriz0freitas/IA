"""
Testes de Integração - Gestor de Frota
"""

import unittest
from testes.test_config import ConfigTestes
from modelo.pedidos import Pedido, EstadoPedido

class TestGestorFrota(unittest.TestCase):
    
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
    
    def test_adicionar_veiculo(self):
        """Testa adição de veículo."""
        self.assertGreater(len(self.gestor.veiculos), 0)
        self.assertIn("E1", self.gestor.veiculos)
    
    def test_veiculos_disponiveis(self):
        """Testa filtragem de veículos disponíveis."""
        disponiveis = self.gestor.veiculos_disponiveis(tempo_atual=0)
        
        self.assertEqual(len(disponiveis), 4)  # 2 elétricos + 2 combustão
    
    def test_calcular_rota(self):
        """Testa cálculo de rota."""
        caminho, custo = self.gestor.calcular_rota("Centro", "Shopping")
        
        self.assertTrue(caminho)
        self.assertGreater(custo, 0.0)
        self.assertEqual(caminho[0], "Centro")
        self.assertEqual(caminho[-1], "Shopping")
    
    def test_verificar_viabilidade_rota(self):
        """Testa verificação de viabilidade."""
        veiculo = self.gestor.veiculos["E1"]
        
        viavel, caminho, custo, distancia = self.gestor.verificar_viabilidade_rota(
            veiculo, "Centro", "Shopping"
        )
        
        self.assertTrue(viavel)
        self.assertTrue(caminho)
        self.assertGreater(distancia, 0.0)
    
    def test_selecionar_veiculo_para_pedido(self):
        """Testa seleção de veículo."""
        pedido = Pedido(
            id_pedido="P_TEST",
            posicao_inicial="Centro",
            posicao_destino="Shopping",
            passageiros=2,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            tempo_max_espera=30
        )
        
        veiculo = self.gestor.selecionar_veiculo_pedido(pedido, tempo_atual=0)
        
        self.assertIsNotNone(veiculo)
        self.assertTrue(veiculo.pode_transportar(2))
    
    def test_filtrar_por_preferencia_eletrico(self):
        """Testa filtro de preferência elétrica."""
        candidatos = self.gestor.veiculos_disponiveis()
        filtrados = self.gestor.filtrar_veiculos_por_preferencia(
            candidatos, "eletrico"
        )
        
        self.assertEqual(len(filtrados), 2)
        for v in filtrados:
            self.assertEqual(v.tipo_veiculo(), "eletrico")
    
    def test_atribuir_pedido(self):
        """Testa atribuição completa de pedido."""
        pedido = Pedido(
            id_pedido="P_TEST2",
            posicao_inicial="Centro",
            posicao_destino="Hospital",
            passageiros=1,
            instante_pedido=0,
            prioridade=2,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            tempo_max_espera=30
        )
        
        self.gestor.adicionar_pedido(pedido)
        veiculo = self.gestor.atribuir_pedido(pedido, tempo_atual=0)
        
        self.assertIsNotNone(veiculo)
        self.assertEqual(pedido.estado, EstadoPedido.ATRIBUIDO)
        self.assertIsNotNone(veiculo.rota)

if __name__ == '__main__':
    unittest.main()