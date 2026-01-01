"""
Testes de Cenários Complexos - Integração Total
"""

import unittest
from gestao.simulador import Simulador
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestCenariosComplexos(unittest.TestCase):
    """Testa cenários realistas com múltiplas variáveis."""
    
    def test_cenario_completo_tudo_ativo(self):
        """
        Cenário completo: trânsito + falhas + pedidos variados.
        """
        gestor = ConfigTestes.criar_gestor_teste()
        simulador = Simulador(
            gestor,
            duracao_total=40,
            usar_transito=True,
            usar_falhas=True,
            prob_falha=0.1
        )
        
        # Mix de pedidos
        pedidos = [
            # Urgente
            Pedido("P_URG", "Centro", "Hospital", 1, 2, 3, 
                  "qualquer", EstadoPedido.PENDENTE, None, None, 10),
            
            # Longas distâncias
            Pedido("P_LONG1", "Porto", "Aeroporto", 2, 5, 2,
                  "eletrico", EstadoPedido.PENDENTE, None, None, 25),
            
            # Grupo ride-sharing
            Pedido("P_RS1", "Centro", "Shopping", 1, 10, 1,
                  "qualquer", EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P_RS2", "Centro", "Shopping", 1, 11, 1,
                  "qualquer", EstadoPedido.PENDENTE, None, None, 20),
            
            # Combustão específico
            Pedido("P_COMB", "Industrial", "Praia", 3, 15, 1,
                  "combustao", EstadoPedido.PENDENTE, None, None, 30),
            
            # Múltiplos simultâneos
            Pedido("P_SIM1", "Universidade", "Estadio", 1, 20, 1,
                  "qualquer", EstadoPedido.PENDENTE, None, None, 15),
            Pedido("P_SIM2", "Praça", "Bairro_Norte1", 2, 20, 2,
                  "eletrico", EstadoPedido.PENDENTE, None, None, 15),
        ]
        
        for p in pedidos:
            simulador.agendar_pedido(p)
        
        # Força falha em estação central
        simulador.gestor_falhas.forcar_falha("Recarga_Centro", tempo_atual=0)
        
        # Executa
        simulador.executar()
        
        # Verificações
        metricas = gestor.metricas.calcular_metricas()
        
        # Deve ter atendido a maioria
        self.assertGreaterEqual(metricas['pedidos_servicos'], 4, 
                               "Deve atender pelo menos 4 dos 7 pedidos")
        
        # Taxa de sucesso razoável mesmo com dificuldades
        self.assertGreater(metricas['taxa_sucesso'], 50.0)
        
        # Deve ter emissões (pedido combustão)
        self.assertGreater(metricas['emissoes_totais'], 0.0)
        
        # Dead mileage deve ser < 70% (eficiência razoável)
        self.assertLess(metricas['perc_km_vazio'], 70.0)
    
    def test_cenario_pico_misto(self):
        """
        Pico de pedidos com preferências ambientais mistas.
        """
        gestor = ConfigTestes.criar_gestor_teste()
        simulador = Simulador(gestor, duracao_total=30)
        
        # 8 pedidos no mesmo instante (pico)
        pedidos_pico = [
            Pedido(f"P{i}", "Centro", "Aeroporto", 1, 10, 
                  i % 3, ["eletrico", "combustao", "qualquer"][i % 3],
                  EstadoPedido.PENDENTE, None, None, 20)
            for i in range(8)
        ]
        
        for p in pedidos_pico:
            simulador.agendar_pedido(p)
        
        simulador.executar()
        
        metricas = gestor.metricas.calcular_metricas()
        
        # Com 4 veículos, não pode atender 8 simultaneamente
        self.assertLessEqual(metricas['pedidos_servicos'], 7)
        
        # Mas deve atender a maioria eventualmente
        self.assertGreaterEqual(metricas['pedidos_servicos'], 5)
    
    def test_cenario_autonomia_critica_multiplos(self):
        """
        Múltiplos veículos com baixa autonomia.
        """
        gestor = ConfigTestes.criar_gestor_teste()
        
        # Reduz autonomia de TODOS
        for v in gestor.veiculos.values():
            v.autonomia_km = 8.0
        
        simulador = Simulador(gestor, duracao_total=30)
        
        # Pedidos que requerem recargas
        pedidos = [
            Pedido(f"P{i}", "Porto", "Aeroporto", 1, i * 5, 2,
                  "eletrico", EstadoPedido.PENDENTE, None, None, 25)
            for i in range(3)
        ]
        
        for p in pedidos:
            simulador.agendar_pedido(p)
        
        simulador.executar()
        
        metricas = gestor.metricas.calcular_metricas()
        
        # Pelo menos 1 deve ser atendido (com recarga)
        self.assertGreater(metricas['pedidos_servicos'], 0)
        
        # Custo total deve incluir recargas
        self.assertGreater(metricas['custo_total'], 5.0)
    
    def test_cenario_falhas_cascata(self):
        """
        Múltiplas estações falham simultaneamente.
        """
        gestor = ConfigTestes.criar_gestor_teste()
        simulador = Simulador(
            gestor, duracao_total=30, 
            usar_falhas=True, prob_falha=0.3
        )
        
        # Força falha em várias estações
        estacoes = simulador.gestor_falhas.obter_estacoes_recarga()
        for estacao in estacoes[:3]:  # 3 primeiras
            simulador.gestor_falhas.forcar_falha(estacao, tempo_atual=0)
        
        # Pedidos elétricos
        pedidos = [
            Pedido(f"P_E{i}", "Centro", "Shopping", 1, i * 3, 1,
                  "eletrico", EstadoPedido.PENDENTE, None, None, 20)
            for i in range(4)
        ]
        
        for p in pedidos:
            simulador.agendar_pedido(p)
        
        # Reduz autonomia
        for v in gestor.veiculos.values():
            if v.tipo_veiculo() == "eletrico":
                v.autonomia_km = 12.0
        
        simulador.executar()
        
        metricas = gestor.metricas.calcular_metricas()
        
        # Sistema deve ser resiliente: usar estações disponíveis
        # ou rejeitar graciosamente
        total = metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']
        self.assertEqual(total, 4, "Deve processar todos os pedidos")
    
    def test_cenario_transito_variavel(self):
        """
        Pedidos ao longo do dia com trânsito variável.
        """
        gestor = ConfigTestes.criar_gestor_teste()
        simulador = Simulador(gestor, duracao_total=60, usar_transito=True)
        
        # Pedidos em diferentes horários
        horarios = [
            (0, "Madrugada"),    # Baixo trânsito
            (480, "Rush manhã"),  # Alto trânsito
            (720, "Almoço"),      # Médio
            (1020, "Rush tarde"), # Alto
        ]
        
        for i, (tempo, periodo) in enumerate(horarios):
            pedido = Pedido(
                f"P_{periodo}", "Centro", "Aeroporto", 
                1, tempo // 60, 1, "qualquer",
                EstadoPedido.PENDENTE, None, None, 30
            )
            simulador.agendar_pedido(pedido)
        
        simulador.executar()
        
        metricas = gestor.metricas.calcular_metricas()
        
        # Todos devem ser atendidos (tempo suficiente)
        self.assertEqual(metricas['pedidos_servicos'], 4)
        
        # Tempo médio deve refletir trânsito variável
        self.assertGreater(metricas['tempo_medio_resposta'], 0)


if __name__ == '__main__':
    unittest.main()