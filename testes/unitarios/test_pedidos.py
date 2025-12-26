"""
Testes Unitários - Pedidos
"""

import unittest
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes

class TestPedidos(unittest.TestCase):
    
    def test_criacao_pedido_valido(self):
        """Testa criação de pedido válido."""
        from modelo.pedidos import Pedido, EstadoPedido
        
        pedido = Pedido(
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
        
        self.assertEqual(pedido.id_pedido, "P1")
        self.assertEqual(pedido.passageiros, 2)
    
    def test_pedido_origem_destino_iguais(self):
        """Testa que origem=destino lança exceção."""
        from modelo.pedidos import Pedido, EstadoPedido
        
        with self.assertRaises(ValueError):
            Pedido(
                id_pedido="P1",
                posicao_inicial="Centro",
                posicao_destino="Centro",
                passageiros=1,
                instante_pedido=0,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
    
    def test_preferencia_ambiental_invalida(self):
        """Testa validação de preferência ambiental."""
        from modelo.pedidos import Pedido, EstadoPedido
        
        with self.assertRaises(ValueError):
            Pedido(
                id_pedido="P1",
                posicao_inicial="A",
                posicao_destino="B",
                passageiros=1,
                instante_pedido=0,
                prioridade=1,
                pref_ambiental="diesel",  # Inválido
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
    
    def test_expirou(self):
        """Testa detecção de pedido expirado."""
        from modelo.pedidos import Pedido, EstadoPedido
        
        pedido = Pedido(
            id_pedido="P1",
            posicao_inicial="A",
            posicao_destino="B",
            passageiros=1,
            instante_pedido=10,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None,
            tempo_max_espera=15
        )
        
        self.assertFalse(pedido.expirou(20))  # 10 min espera
        self.assertTrue(pedido.expirou(30))   # 20 min espera > 15

if __name__ == '__main__':
    unittest.main()