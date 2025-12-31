"""
Testes Avançados - Estrutura do Grafo
"""

import unittest
from modelo.grafo import Grafo, No, Aresta, TipoNo
from testes.test_config import ConfigTestes


class TestGrafoAvancado(unittest.TestCase):
    """Testa propriedades avançadas do grafo."""
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        self.grafo = ConfigTestes.criar_grafo_teste()
    
    def test_conectividade_completa(self):
        """Testa que todos os nós são alcançáveis."""
        from gestao.algoritmos_procura.bfs import bfs
        
        # Centro deve alcançar todos os outros nós
        falhas = []
        for no_id in self.grafo.nos.keys():
            if no_id == "Centro":
                continue
            
            caminho = bfs(self.grafo, "Centro", no_id)
            if not caminho:
                falhas.append(no_id)
        
        self.assertEqual(len(falhas), 0, 
                        f"Nós não alcançáveis a partir do Centro: {falhas}")
    
    def test_simetria_arestas(self):
        """Testa que todas as arestas são bidirecionais."""
        for origem, arestas in self.grafo.adjacentes.items():
            for aresta in arestas:
                destino = aresta.no_destino
                
                # Verifica que existe aresta reversa
                aresta_reversa = None
                try:
                    aresta_reversa = self.grafo.get_aresta(destino, origem)
                except ValueError:
                    pass
                
                self.assertIsNotNone(
                    aresta_reversa,
                    f"Aresta {origem}→{destino} não tem reversa {destino}→{origem}"
                )
                
                # Verifica que distâncias são iguais
                self.assertAlmostEqual(
                    aresta.distancia_km,
                    aresta_reversa.distancia_km,
                    places=2,
                    msg=f"Distâncias assimétricas: {origem}↔{destino}"
                )
    
    def test_distribuicao_tipos_nos(self):
        """Testa distribuição adequada de tipos de nós."""
        tipos = {}
        for no in self.grafo.nos.values():
            tipos[no.tipo] = tipos.get(no.tipo, 0) + 1
        
        total = len(self.grafo.nos)
        
        # Deve ter pelo menos:
        # - 50% zonas de recolha
        # - 15% estações de recarga
        # - 10% postos de abastecimento
        
        recolha = tipos.get(TipoNo.RECOLHA_PASSAGEIROS, 0)
        recarga = tipos.get(TipoNo.ESTACAO_RECARGA, 0)
        postos = tipos.get(TipoNo.POSTO_ABASTECIMENTO, 0)
        
        self.assertGreaterEqual(recolha / total, 0.5, 
                               "Zonas de recolha devem ser ≥50% do total")
        self.assertGreaterEqual(recarga, 3, 
                               "Deve haver pelo menos 3 estações de recarga")
        self.assertGreaterEqual(postos, 2, 
                               "Deve haver pelo menos 2 postos de abastecimento")
    
    def test_densidade_conexoes(self):
        """Testa que o grafo não é muito esparso."""
        total_nos = len(self.grafo.nos)
        total_arestas = sum(len(adj) for adj in self.grafo.adjacentes.values()) // 2
        
        # Densidade = arestas / arestas_possíveis
        arestas_possiveis = (total_nos * (total_nos - 1)) // 2
        densidade = total_arestas / arestas_possiveis
        
        # Grafo urbano: densidade entre 10% e 40%
        self.assertGreater(densidade, 0.10, 
                          "Grafo muito esparso (densidade < 10%)")
        self.assertLess(densidade, 0.40, 
                       "Grafo muito denso (densidade > 40%)")
    
    def test_grau_minimo_nos(self):
        """Testa que todos os nós têm conexões mínimas."""
        graus_baixos = []
        
        for no_id, arestas in self.grafo.adjacentes.items():
            grau = len(arestas)
            
            # Cada nó deve ter pelo menos 2 conexões (evitar "becos sem saída")
            if grau < 2:
                graus_baixos.append((no_id, grau))
        
        self.assertEqual(len(graus_baixos), 0,
                        f"Nós com grau < 2: {graus_baixos}")
    
    def test_distancia_realista(self):
        """Testa que distâncias são realistas."""
        distancias_irrealistas = []
        
        for origem, arestas in self.grafo.adjacentes.items():
            for aresta in arestas:
                # Distância entre 0.1 km e 10 km é razoável para cidade
                if aresta.distancia_km < 0.1 or aresta.distancia_km > 10.0:
                    distancias_irrealistas.append(
                        (origem, aresta.no_destino, aresta.distancia_km)
                    )
        
        self.assertEqual(len(distancias_irrealistas), 0,
                        f"Distâncias irrealistas: {distancias_irrealistas}")
    
    def test_tempo_viagem_coerente(self):
        """Testa que tempo de viagem é coerente com distância."""
        incoerencias = []
        
        for origem, arestas in self.grafo.adjacentes.items():
            for aresta in arestas:
                # Velocidade implícita: 10-60 km/h é razoável
                velocidade_kmh = (aresta.distancia_km / aresta.tempoViagem_min) * 60
                
                if velocidade_kmh < 10 or velocidade_kmh > 70:
                    incoerencias.append(
                        (origem, aresta.no_destino, 
                         f"{velocidade_kmh:.1f} km/h")
                    )
        
        self.assertEqual(len(incoerencias), 0,
                        f"Velocidades implícitas incoerentes: {incoerencias}")
    
    def test_cobertura_estacoes(self):
        """Testa que estações cobrem a cidade adequadamente."""
        from gestao.algoritmos_procura.a_estrela import a_star_search
        
        # Encontra todas as estações de recarga
        estacoes = [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo == TipoNo.ESTACAO_RECARGA
        ]
        
        # Zonas de recolha
        zonas = [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo == TipoNo.RECOLHA_PASSAGEIROS
        ]
        
        # Verifica que cada zona tem estação a menos de 15 km
        zonas_sem_cobertura = []
        
        for zona in zonas[:5]:  # Testa apenas 5 para não demorar
            dist_minima = float('inf')
            
            for estacao in estacoes:
                custo, caminho = a_star_search(self.grafo, zona, estacao)
                if caminho:
                    # Calcula distância real
                    dist = 0
                    for i in range(len(caminho) - 1):
                        aresta = self.grafo.get_aresta(caminho[i], caminho[i+1])
                        dist += aresta.distancia_km
                    
                    dist_minima = min(dist_minima, dist)
            
            if dist_minima > 15.0:
                zonas_sem_cobertura.append((zona, dist_minima))
        
        self.assertEqual(len(zonas_sem_cobertura), 0,
                        f"Zonas sem estação próxima: {zonas_sem_cobertura}")


if __name__ == '__main__':
    unittest.main()