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
    
    def test_transito_aumenta_tempos(self):
        """Verifica que trânsito aumenta tempos de viagem."""
        grafo = self.simulador.gestor.grafo
        
        # Salva tempo base (sem trânsito aplicado ainda)
        aresta_ref = grafo.get_aresta("Centro", "Shopping")
        tempo_base = aresta_ref.tempoViagem_min
        
        # Madrugada (2h) - fator 0.8
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=120)
        aresta_noite = grafo.get_aresta("Centro", "Shopping")
        tempo_noturno = aresta_noite.tempo_real()
        
        # Rush hour (8h) - fator 1.8 (com aumento adicional para zona central)
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)
        aresta_rush = grafo.get_aresta("Centro", "Shopping")
        tempo_rush = aresta_rush.tempo_real()
        
        # Noite: fator 0.8 = redução (mas aresta tem congestion aplicado)
        self.assertAlmostEqual(tempo_noturno, tempo_base * 0.8, delta=tempo_base * 0.1, 
                              msg=f"Noite ({tempo_noturno:.2f}) vs Base ({tempo_base:.2f})")
        
        # Rush: fator >= 1.8 (Centro é zona central, recebe multiplicador adicional)
        self.assertGreater(tempo_rush, tempo_base * 1.5, 
                          f"Rush ({tempo_rush:.2f}) deveria aumentar vs Base ({tempo_base:.2f})")
        
        # Rush deve ser maior que noite
        self.assertGreater(tempo_rush, tempo_noturno, 
                          f"Rush ({tempo_rush:.2f}) deveria ser > Noite ({tempo_noturno:.2f})")
        
    def test_pedidos_atendidos_com_transito(self):
        """Testa que pedidos são atendidos mesmo com trânsito."""
        for i in range(5):
            pedido = Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Shopping",
                passageiros=1,
                instante_pedido=i * 2, 
                prioridade=2,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,
                tempo_max_espera=None
            )
            self.simulador.agendar_pedido(pedido)
        
        # Aplica congestionamento
        self.simulador.gestor_transito.atualizar_transito(tempo_simulacao=480)
        
        self.simulador.executar()
        
        metricas = self.gestor.metricas.calcular_metricas()
        self.assertGreater(metricas['pedidos_servicos'], 0)


if __name__ == '__main__':
    unittest.main()