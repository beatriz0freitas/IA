"""
Fábrica de grafos de demonstração para a simulação TaxiGreen.
Layout Urbano Realista:
- Centro: Alta densidade de zonas de recolha (escritórios, comércio)
- Periferia: Zonas residenciais e industriais
- Estações de recarga: Distribuídas estrategicamente
- Postos de abastecimento: Nas entradas/saídas da cidade

        Cria grafo urbano com 30 nós representando:
        - 18 zonas de recolha (60%)
        - 7 estações de recarga (23%) 
        - 5 postos de abastecimento (17%)
        
        Layout:
              Periferia Norte
                  |
        Oeste -- CENTRO -- Este
                  |
              Periferia Sul
"""

from modelo.grafo import Grafo, No, TipoNo

class GrafoDemo:
    @staticmethod
    def criar_grafo_demo() -> Grafo:

        g = Grafo()
        coordenadas = {
            # ========== CENTRO (y: 4.5-7.5, x: 4.5-7.5) ==========
            "Centro": (6, 6, TipoNo.RECOLHA_PASSAGEIROS),
            "Praça": (6, 7.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Estação_Metro": (7.5, 6, TipoNo.RECOLHA_PASSAGEIROS),
            "Shopping": (4.5, 6, TipoNo.RECOLHA_PASSAGEIROS),
            "Hospital": (7.5, 7.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Universidade": (4.5, 7.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Centro": (6, 4.5, TipoNo.ESTACAO_RECARGA),

            # ========== NORTE (y: 9-12) ==========
            "Bairro_Norte1": (4.5, 10.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Bairro_Norte2": (7.5, 10.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Escola_Norte": (6, 12, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Norte": (6, 9, TipoNo.ESTACAO_RECARGA),
            "Posto_Norte": (4.5, 12, TipoNo.POSTO_ABASTECIMENTO),

            # ========== SUL (y: 0-3) ==========
            "Industrial": (4.5, 1.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Bairro_Sul": (7.5, 1.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Porto": (6, 0, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Sul": (6, 3, TipoNo.ESTACAO_RECARGA),
            "Posto_Sul": (7.5, 0, TipoNo.POSTO_ABASTECIMENTO),

            # ========== OESTE (x: 0-3) ==========
            "Suburbio_Oeste1": (1.5, 6, TipoNo.RECOLHA_PASSAGEIROS),
            "Suburbio_Oeste2": (0, 7.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Centro_Comercial_Oeste": (3, 4.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Oeste": (1.5, 4.5, TipoNo.ESTACAO_RECARGA),
            "Posto_Oeste": (0, 6, TipoNo.POSTO_ABASTECIMENTO),

            # ========== ESTE (x: 9-12) ==========
            "Parque_Tec": (10.5, 6, TipoNo.RECOLHA_PASSAGEIROS),
            "Aeroporto": (12, 4.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Bairro_Este": (9, 7.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Este": (10.5, 4.5, TipoNo.ESTACAO_RECARGA),
            "Posto_Este": (12, 6, TipoNo.POSTO_ABASTECIMENTO),

            # ========== CONEXÕES PERIFÉRICAS ==========
            "Estadio": (3, 9, TipoNo.RECOLHA_PASSAGEIROS),
            "Praia": (9, 1.5, TipoNo.RECOLHA_PASSAGEIROS),
            "Recarga_Estadio": (3, 10.5, TipoNo.ESTACAO_RECARGA),
            "Recarga_Praia": (10.5, 3, TipoNo.ESTACAO_RECARGA),
    }

        # Adiciona todos os nós
        for nid, (x, y, tipo) in coordenadas.items():
            g.adiciona_no(No(nid, x, y, tipo))

        # ==========================================================
        # REDE VIÁRIA (conexões realistas)
        # ==========================================================
        
        conexoes = [
            # ===== ANEL CENTRAL (conexão circular centro) =====
            ("Centro", "Praça", 0.8),
            ("Centro", "Shopping", 0.9),
            ("Centro", "Estação_Metro", 0.7),
            ("Praça", "Hospital", 1.0),
            ("Praça", "Universidade", 1.1),
            ("Estação_Metro", "Hospital", 0.8),
            ("Shopping", "Universidade", 1.0),
            
            # Ligações centro ↔ estação recarga central
            ("Centro", "Recarga_Centro", 0.6),
            ("Recarga_Centro", "Shopping", 1.2),
            ("Recarga_Centro", "Estação_Metro", 1.3),
            
            # ===== EIXO NORTE-SUL (avenida principal) =====
            ("Praça", "Recarga_Norte", 1.5),
            ("Recarga_Norte", "Bairro_Norte1", 1.8),
            ("Recarga_Norte", "Bairro_Norte2", 2.0),
            ("Bairro_Norte1", "Estadio", 1.5),
            ("Bairro_Norte1", "Escola_Norte", 1.2),
            ("Bairro_Norte2", "Escola_Norte", 1.3),
            ("Escola_Norte", "Posto_Norte", 0.8),
            ("Estadio", "Recarga_Estadio", 0.5),
            ("Estadio", "Posto_Norte", 2.0),
            
            ("Recarga_Centro", "Recarga_Sul", 1.8),
            ("Recarga_Sul", "Industrial", 1.5),
            ("Recarga_Sul", "Bairro_Sul", 1.4),
            ("Industrial", "Porto", 1.0),
            ("Bairro_Sul", "Porto", 1.2),
            ("Porto", "Posto_Sul", 0.7),
            ("Bairro_Sul", "Praia", 2.5),
            ("Praia", "Recarga_Praia", 0.6),
            
            # ===== EIXO OESTE-ESTE (via rápida) =====
            ("Posto_Oeste", "Suburbio_Oeste2", 0.5),
            ("Suburbio_Oeste2", "Suburbio_Oeste1", 1.2),
            ("Suburbio_Oeste1", "Recarga_Oeste", 0.8),
            ("Recarga_Oeste", "Centro_Comercial_Oeste", 1.0),
            ("Centro_Comercial_Oeste", "Shopping", 1.5),
            ("Shopping", "Centro", 0.9),
            ("Centro", "Estação_Metro", 0.7),
            ("Estação_Metro", "Bairro_Este", 2.2),
            ("Bairro_Este", "Parque_Tec", 1.3),
            ("Parque_Tec", "Recarga_Este", 0.9),
            ("Recarga_Este", "Aeroporto", 1.5),
            ("Aeroporto", "Posto_Este", 0.6),
            
            # ===== CONEXÕES TRANSVERSAIS =====
            # Norte-Oeste
            ("Universidade", "Estadio", 2.0),
            ("Suburbio_Oeste1", "Bairro_Norte1", 2.5),
            
            # Norte-Este
            ("Hospital", "Bairro_Norte2", 1.8),
            ("Bairro_Norte2", "Bairro_Este", 3.0),
            
            # Sul-Oeste
            ("Centro_Comercial_Oeste", "Industrial", 2.3),
            ("Suburbio_Oeste2", "Industrial", 3.5),
            
            # Sul-Este
            ("Hospital", "Praia", 3.8),
            ("Estação_Metro", "Recarga_Praia", 3.2),
            ("Bairro_Este", "Praia", 2.8),
            
            # Conexões com aeroporto (zona periférica)
            ("Parque_Tec", "Bairro_Este", 1.3),
            ("Recarga_Praia", "Posto_Sul", 2.5),
            
            # Anel periférico (bypass da cidade)
            ("Posto_Norte", "Posto_Oeste", 4.5),
            ("Posto_Oeste", "Posto_Sul", 4.2),
            ("Posto_Sul", "Posto_Este", 4.8),
            ("Posto_Este", "Posto_Norte", 5.0),
        ]

        # Adiciona todas as arestas
        for origem, destino, dist_km in conexoes:
            # Velocidade média urbana: 30 km/h
            # Velocidade em vias rápidas/periféricas: 50 km/h
            
            # Determina velocidade baseada na localização
            velocidade_kmh = 30  # padrão
            
            # Vias rápidas (conexões longas > 3km ou postos na periferia)
            if dist_km > 3.0 or "Posto" in origem or "Posto" in destino:
                velocidade_kmh = 50
            # Centro congestionado
            elif any(zona in origem or zona in destino 
                    for zona in ["Centro", "Praça", "Shopping", "Estação_Metro"]):
                velocidade_kmh = 20
            
            tempo_min = (dist_km / velocidade_kmh) * 60
            g.adiciona_aresta(origem, destino, dist_km, tempo_min)

        print(f"\n TaxiGreen City criada:")
        print(f" {len(g.nos)} zonas")
        print(f" {sum(len(adj) for adj in g.adjacentes.values()) // 2} ligações")
        
        # Estatísticas por tipo
        tipos = {}
        for no in g.nos.values():
            tipos[no.tipo] = tipos.get(no.tipo, 0) + 1
        
        return g
