"""
Testes de Integração - Gestor de Falhas
"""

import unittest
from testes.test_config import ConfigTestes
from gestao.gestor_falhas import GestorFalhas

class TestGestorFalhas(unittest.TestCase):
    
    def setUp(self):
        from gestao.gestor_falhas import GestorFalhas
        
        self.grafo = ConfigTestes.criar_grafo_teste()
        self.gestor_falhas = GestorFalhas(self.grafo, prob_falha=0.3)
    
    def test_obter_estacoes_recarga(self):
        """Testa listagem de estações de recarga."""
        estacoes = self.gestor_falhas.obter_estacoes_recarga()
        
        self.assertGreater(len(estacoes), 0)
        self.assertIn("Recarga_Centro", estacoes)
    
    def test_obter_postos_abastecimento(self):
        """Testa listagem de postos."""
        postos = self.gestor_falhas.obter_postos_abastecimento()
        
        self.assertGreater(len(postos), 0)
    
    def test_forcar_falha(self):
        """Testa forçar falha em estação específica."""
        sucesso = self.gestor_falhas.forcar_falha("Recarga_Centro", tempo_atual=10)
        
        self.assertTrue(sucesso)
        
        no = self.grafo.nos["Recarga_Centro"]
        self.assertFalse(no.disponivel)
    
    def test_recuperar_estacao(self):
        """Testa recuperação de estação."""
        self.gestor_falhas.forcar_falha("Recarga_Centro", tempo_atual=10)
        self.gestor_falhas.recuperar_estacao("Recarga_Centro", tempo_atual=15)
        
        no = self.grafo.nos["Recarga_Centro"]
        self.assertTrue(no.disponivel)
    
    def test_simular_falha_aleatoria(self):
        """Testa simulação de falhas aleatórias."""
        import random
        
        # Define seed para tornar teste determinístico
        random.seed(42)
        
        # Com prob=0.3 e seed=42, deve haver falhas
        falhas_primeira = self.gestor_falhas.simular_falha_aleatoria(tempo_atual=20)
        
        # Reset seed e testa novamente
        random.seed(42)
        falhas_segunda = self.gestor_falhas.simular_falha_aleatoria(tempo_atual=20)
        
        # Com mesmo seed, deve ter mesmo resultado (determinístico)
        self.assertEqual(len(falhas_primeira), len(falhas_segunda),
                        "Com mesmo seed, deve ter mesmo número de falhas")
        
        # Testa que método retorna lista
        self.assertIsInstance(falhas_primeira, list)
        
        # Remove seed para não afetar outros testes
        random.seed()

    def test_obter_estado_estacoes(self):
        """Testa estado global das estações."""
        estado = self.gestor_falhas.obter_estado_estacoes()
        
        self.assertIn("estacoes_recarga", estado)
        self.assertIn("postos_abastecimento", estado)
        self.assertIn("total_falhas_historico", estado)
    
    def test_historico_falhas(self):
        """Testa registro de histórico."""
        self.gestor_falhas.forcar_falha("Recarga_Centro", tempo_atual=10)
        self.gestor_falhas.recuperar_estacao("Recarga_Centro", tempo_atual=15)
        
        self.assertGreater(len(self.gestor_falhas.historico_falhas), 0)
        
        # Verifica que eventos estão registrados
        tipos = [e['tipo'] for e in self.gestor_falhas.historico_falhas]
        self.assertIn("FALHA_FORCADA", tipos)
        self.assertIn("RECUPERACAO_MANUAL", tipos)


if __name__ == '__main__':
    unittest.main()
