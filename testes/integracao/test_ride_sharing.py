"""
Testes de integração do sistema de ride-sharing.
"""

import unittest
from gestao.ride_sharing import GestorRideSharing
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestRideSharing(unittest.TestCase):
    """Testa agrupamento de pedidos para ride-sharing."""
    
    def setUp(self):
        """Setup comum."""
        self.grafo = ConfigTestes.criar_grafo_teste()
        self.gestor_rs = GestorRideSharing(
            self.grafo,
            raio_agrupamento_km=2.0,
            janela_temporal_min=5
        )
        self.gestor_frota = ConfigTestes.criar_gestor_teste()
    
    def test_pedidos_compativeis_espacialmente(self):
        """Testa identificação de pedidos próximos."""
        p1 = Pedido(
            id_pedido="P1",
            posicao_inicial="Centro",
            posicao_destino="Praça",
            passageiros=2,
            instante_pedido=10,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )

        p2 = Pedido(
            id_pedido="P2",
            posicao_inicial="Centro",
            posicao_destino="Praça",
            passageiros=1,
            instante_pedido=12,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )

        # Mesma origem, mesmo destino - compatível espacialmente
        compativel = self.gestor_rs.pedidos_compativel_espacial(p1, p2)
        self.assertTrue(compativel)
    
    def test_encontrar_grupos(self):
        """Testa formação de grupos de pedidos."""
        pedidos = [
            Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
            for i in range(3)
        ]
        
        grupos = self.gestor_rs.encontrar_grupos_compativeis(pedidos)
        
        # Deve criar pelo menos um grupo
        self.assertGreater(len(grupos), 0)
        
        # Grupo deve ter 2+ pedidos
        grupo = grupos[0]
        self.assertGreaterEqual(len(grupo.pedidos), 2)
    
    def test_respeita_capacidade(self):
        """Testa que grupos respeitam capacidade."""
        pedidos = [
            Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=3,  # 3 passageiros cada
                instante_pedido=i,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
            for i in range(3)
        ]
        
        # Capacidade = 4, não deve agrupar 2 pedidos de 3 passageiros
        grupos = self.gestor_rs.encontrar_grupos_compativeis(pedidos, capacidade_maxima=4)
        
        for grupo in grupos:
            self.assertLessEqual(grupo.passageiros_total, 4)
    
    def test_economia_calculada(self):
        """Testa cálculo de economia de km."""
        pedidos = [
            Pedido(
                id_pedido="P1",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=0,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            ),
            Pedido(
                id_pedido="P2",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=1,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
        ]
        
        grupos = self.gestor_rs.encontrar_grupos_compativeis(pedidos)
        
        if grupos:
            grupo = grupos[0]
            # Economia deve ser positiva (2 viagens → 1 viagem)
            self.assertGreater(grupo.economia_estimada, 0)


if __name__ == '__main__':
    unittest.main()