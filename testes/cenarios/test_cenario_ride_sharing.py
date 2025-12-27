"""
Testes de Cenários - Ride-Sharing Ativo
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes
from gestao.ride_sharing import GestorRideSharing

class TestCenarioRideSharing(unittest.TestCase):
    
    def setUp(self):
        from gestao.ride_sharing import GestorRideSharing
        
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=False,
            usar_falhas=False
        )
        
        self.gestor_rs = GestorRideSharing(
            self.gestor.grafo,
            raio_agrupamento_km=3.0,
            janela_temporal_min=5
        )
    
    def test_agrupar_pedidos_proximos(self):
        """Testa agrupamento de pedidos próximos."""
        # Cria pedidos próximos espacialmente e temporalmente
        pedidos = []
        for i in range(4):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            pedidos.append(pedido)
            self.simulador.agendar_pedido(pedido)
        
        # Busca grupos
        grupos = self.gestor_rs.encontrar_grupos_compativeis(pedidos)
        
        # Deve criar pelo menos um grupo
        self.assertGreater(len(grupos), 0)
        
        # Grupo deve ter múltiplos pedidos
        if grupos:
            self.assertGreaterEqual(len(grupos[0].pedidos), 2)
    
    def test_economia_km(self):
        """Testa que ride-sharing economiza km."""
        pedidos = []
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=30
            )
            pedidos.append(pedido)
        
        grupos = self.gestor_rs.encontrar_grupos_compativeis(pedidos)
        
        if grupos:
            grupo = grupos[0]
            # Economia deve ser positiva
            self.assertGreater(grupo.economia_estimada, 0.0)

if __name__ == '__main__':
    unittest.main()