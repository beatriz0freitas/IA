"""
Testes de Reposicionamento Proativo
"""

import unittest
from gestao.reposicionamento import reposicionar_veiculo_proativo
from modelo.veiculos import VeiculoEletrico, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from testes.test_config import ConfigTestes


class TestReposicionamento(unittest.TestCase):
    """Testa sistema de reposicionamento proativo."""
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        self.grafo = ConfigTestes.criar_grafo_teste()
        
        self.veiculo = VeiculoEletrico(
            id_veiculo="E1",
            posicao="Porto",  # Longe do centro
            autonomia_km=60.0,
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
    
    def test_identifica_zona_alta_procura(self):
        """Testa identificação de zona com alta procura."""
        # Cria pedidos concentrados no Centro
        pedidos_futuros = [
            Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Centro",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i + 5,  # Próximos 3 minutos
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
            for i in range(3)
        ]
        
        zona_alvo = reposicionar_veiculo_proativo(
            self.veiculo,
            pedidos_futuros,
            tempo_atual=0,
            grafo=self.grafo,
            janela_previsao=10
        )
        
        # Deve sugerir Centro (3 pedidos)
        self.assertEqual(zona_alvo, "Centro")
    
    def test_sem_pedidos_futuros(self):
        """Testa comportamento sem pedidos futuros."""
        zona_alvo = reposicionar_veiculo_proativo(
            self.veiculo,
            [],  # Sem pedidos
            tempo_atual=0,
            grafo=self.grafo,
            janela_previsao=10
        )
        
        # Deve ficar onde está
        self.assertEqual(zona_alvo, self.veiculo.posicao)
    
    def test_pedidos_fora_janela(self):
        """Testa que ignora pedidos fora da janela de previsão."""
        # Pedidos muito distantes no futuro
        pedidos_distantes = [
            Pedido(
                id_pedido=f"P{i}",
                posicao_inicial="Shopping",
                posicao_destino="Aeroporto",
                passageiros=1,
                instante_pedido=i + 50,  # Muito no futuro
                prioridade=1,
                pref_ambiental="qualquer",
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None
            )
            for i in range(5)
        ]
        
        zona_alvo = reposicionar_veiculo_proativo(
            self.veiculo,
            pedidos_distantes,
            tempo_atual=0,
            grafo=self.grafo,
            janela_previsao=10  # Janela de 10 minutos
        )
        
        # Não deve considerar pedidos no instante 50+
        self.assertEqual(zona_alvo, self.veiculo.posicao)
    
    def test_multiplas_zonas_procura(self):
        """Testa seleção entre múltiplas zonas com procura."""
        pedidos_futuros = [
            # 2 no Centro
            Pedido("P1", "Centro", "A", 1, 5, 1, "qualquer", EstadoPedido.PENDENTE, None),
            Pedido("P2", "Centro", "B", 1, 7, 1, "qualquer", EstadoPedido.PENDENTE, None),
            
            # 3 no Shopping (mais procura)
            Pedido("P3", "Shopping", "C", 1, 6, 1, "qualquer", EstadoPedido.PENDENTE, None),
            Pedido("P4", "Shopping", "D", 1, 8, 1, "qualquer", EstadoPedido.PENDENTE, None),
            Pedido("P5", "Shopping", "E", 1, 9, 1, "qualquer", EstadoPedido.PENDENTE, None),
        ]
        
        zona_alvo = reposicionar_veiculo_proativo(
            self.veiculo,
            pedidos_futuros,
            tempo_atual=0,
            grafo=self.grafo,
            janela_previsao=15
        )
        
        # Deve escolher Shopping (3 pedidos vs 2)
        self.assertEqual(zona_alvo, "Shopping")
    
    def test_janela_previsao_personalizada(self):
        """Testa ajuste de janela de previsão."""
        pedidos = [
            Pedido("P1", "Hospital", "X", 1, 5, 1, "qualquer", EstadoPedido.PENDENTE, None),
            Pedido("P2", "Hospital", "Y", 1, 25, 1, "qualquer", EstadoPedido.PENDENTE, None),
        ]
        
        # Janela curta (10 min) - só considera P1
        zona_curta = reposicionar_veiculo_proativo(
            self.veiculo, pedidos, 0, self.grafo, janela_previsao=10
        )
        
        # Janela longa (30 min) - considera ambos
        zona_longa = reposicionar_veiculo_proativo(
            self.veiculo, pedidos, 0, self.grafo, janela_previsao=30
        )
        
        # Ambas devem apontar para Hospital
        self.assertEqual(zona_curta, "Hospital")
        self.assertEqual(zona_longa, "Hospital")


if __name__ == '__main__':
    unittest.main()