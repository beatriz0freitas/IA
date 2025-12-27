"""
Teste de cenário: Rush Hour com trânsito intenso.
"""

import unittest
from gestao.simulador import Simulador
from gestao.transito_dinamico import GestorTransito
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestCenarioRushHour(unittest.TestCase):
    
    def setUp(self):
        self.gestor = ConfigTestes.criar_gestor_teste()
        self.simulador = Simulador(
            self.gestor,
            duracao_total=30,
            usar_transito=True,
            usar_falhas=False
        )
        
        # Configura hora do rush (8h da manhã = 480 minutos)
        self.simulador.tempo_atual = 480
        self.simulador.gestor_transito.atualizar_transito(480)
    
    def test_transito_aumenta_tempos(self):
        """Verifica que trânsito aumenta tempos de viagem."""
        grafo = self.simulador.gestor.grafo
        
        # Centro -> Shopping é conexão direta e central (afetada por trânsito)
        
        # Sem congestionamento (madrugada - 2h)
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=120)  # 2h
        aresta_noite = grafo.get_aresta("Centro", "Shopping")
        custo_noturno = aresta_noite.tempo_real()
        
        # Com rush hour (8h da manhã)
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)  # 8h
        aresta_rush = grafo.get_aresta("Centro", "Shopping")
        custo_rush = aresta_rush.tempo_real()
        
        # Rush hour deve aumentar tempo (zona central sofre mais)
        self.assertGreater(custo_rush, custo_noturno,
                          f"Rush ({custo_rush:.2f}) deveria ser > Noite ({custo_noturno:.2f})")
    
    def test_pedidos_atendidos_com_transito(self):
        """Testa que pedidos são atendidos mesmo com trânsito."""
        # Cria pedidos
        for i in range(5):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i,
                prioridade=2,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=None
            )
            self.simulador.agendar_pedido(pedido)
        
        # Executa simulação
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        
        # Deve atender pelo menos alguns pedidos
        self.assertGreater(metricas['pedidos_servicos'], 0)


if __name__ == '__main__':
    unittest.main()