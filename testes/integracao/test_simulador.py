"""
Testes de Integração - Simulador
"""

import unittest
from testes.test_config import ConfigTestes
from modelo.pedidos import Pedido, EstadoPedido
from gestao.simulador import Simulador
from gestao.gestor_frota import GestorFrota
from gestao.gestor_falhas import GestorFalhas
from gestao.ride_sharing import GestorRideSharing
from gestao.estrategia_selecao import SelecaoMenorDistancia
from gestao.funcao_custo import FuncaoCustoComposta


class TestSimulador(unittest.TestCase):
    
    def setUp(self):
        from gestao.simulador import Simulador
        
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=20,
            usar_transito=False,
            usar_falhas=False
        )
    
    def test_agendar_pedido(self):
        """Testa agendamento de pedido."""
        pedido = Pedido(
            id_pedido="P_SIM",
            posicao_inicial="Centro",
            posicao_destino="Shopping",
            passageiros=1,
            instante_pedido=5,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )
        
        self.simulador.agendar_pedido(pedido)
        
        self.assertEqual(len(self.simulador.fila_pedidos), 1)
        self.assertIn(pedido, self.simulador.pedidos_todos)
    
    def test_processar_pedidos_novos(self):
        """Testa processamento de novos pedidos."""
        pedido = Pedido(
            id_pedido="P_PROC",
            posicao_inicial="Centro",
            posicao_destino="Shopping",
            passageiros=1,
            instante_pedido=0,
            prioridade=1,
            pref_ambiental="qualquer",
            estado=EstadoPedido.PENDENTE,
            veiculo_atribuido=None
        )
        
        self.simulador.agendar_pedido(pedido)
        self.simulador.tempo_atual = 0
        self.simulador.processar_pedidos_novos()
        
        self.assertIn(pedido, self.gestor.pedidos_pendentes)
    
    def test_simulacao_completa_curta(self):
        """Testa execução de simulação curta."""
        # Adiciona alguns pedidos
        for i in range(3):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 2,
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=20
            )
            self.simulador.agendar_pedido(pedido)
        
        # Executa simulação
        self.simulador.executar()
        
        # Verifica que simulação concluiu
        self.assertGreater(self.simulador.tempo_atual, self.simulador.duracao_total)
        
        # Verifica métricas
        metricas = self.gestor.metricas.calcular_metricas()
        total_pedidos = metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']
        self.assertEqual(total_pedidos, 3)

if __name__ == '__main__':
    unittest.main()