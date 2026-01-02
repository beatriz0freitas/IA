"""
Sistema de gestão de trânsito dinâmico.
Simula variação de congestionamento por hora do dia e zona.
"""

from typing import Dict, List
import random
from modelo.grafo import Grafo


class GestorTransito:
    """
    Gere o congestionamento dinâmico do grafo.

    Padrões de trânsito:
    - Rush hour manhã: 7-10h (factor 1.5-2.0)
    - Hora de almoço: 12-14h (factor 1.3)
    - Rush hour tarde: 17-20h (factor 1.5-2.0)
    - Noite/madrugada: 22-6h (factor 0.8)
    """

    def __init__(self, grafo: Grafo, hora_inicial: int = None):
        self.grafo = grafo
        # Hora inicial aleatória se não especificada (0-23h)
        self.hora_inicial = hora_inicial if hora_inicial is not None else random.randint(0, 23)
        self.hora_atual = self.hora_inicial

        # Zonas com maior congestionamento
        self.zonas_centro = [
            "Centro", "Praça", "Shopping", "Estação_Metro",
            "Hospital", "Universidade"
        ]

        self.zonas_comerciais = [
            "Centro_Comercial_Oeste", "Parque_Tec", "Aeroporto"
        ]


    def atualizar_hora(self, minutos_simulacao: int):
        """
        Atualiza hora do dia com base nos minutos de simulação.
        Assume que 1 minuto de simulação = 1 minuto real.
        """
        self.hora_atual = (self.hora_inicial + (minutos_simulacao // 60)) % 24


    def calcular_factor_hora(self, hora: int) -> float:
        """
        Calcula factor de congestionamento base por hora do dia.

        Returns:
            Factor multiplicador (0.8 a 2.0)
        """
        if 7 <= hora <= 9:  # Rush manhã
            return 1.8
        elif hora == 10:  # Final rush manhã
            return 1.4
        elif 12 <= hora <= 13:  # Hora almoço
            return 1.3
        elif 17 <= hora <= 19:  # Rush tarde
            return 2.0
        elif hora == 20:  # Final rush tarde
            return 1.5
        elif 22 <= hora or hora <= 6:  # Noite/madrugada
            return 0.8
        else:  # Horas normais
            return 1.0


    def eh_zona_central(self, no_id: str) -> bool:
        """Verifica se nó está em zona central (maior congestionamento)"""
        return any(zona in no_id for zona in self.zonas_centro)


    def eh_zona_comercial(self, no_id: str) -> bool:
        """Verifica se nó está em zona comercial"""
        return any(zona in no_id for zona in self.zonas_comerciais)


    def atualizar_transito(self, tempo_simulacao: int = 0):
        """
        Atualiza congestionamento de todas as arestas com base na hora atual.

        Args:
            tempo_simulacao: Minutos desde início da simulação
        """
        self.atualizar_hora(tempo_simulacao)
        factor_base = self.calcular_factor_hora(self.hora_atual)

        for no_origem, arestas in self.grafo.adjacentes.items():
            for aresta in arestas:
                no_destino = aresta.no_destino

                # Reinicia factor (não acumula)
                factor = factor_base

                # Aumenta congestionamento em zonas centrais durante rush hour
                if (self.eh_zona_central(no_origem) or self.eh_zona_central(no_destino)):
                    if factor > 1.0:  # Só aumenta se já houver trânsito
                        factor *= 1.2

                # Aeroporto/zonas comerciais têm pico ao fim do dia
                if (self.eh_zona_comercial(no_origem) or self.eh_zona_comercial(no_destino)):
                    if 17 <= self.hora_atual <= 19:
                        factor *= 1.15

                # SUBSTITUI congestionamento (não multiplica o anterior)
                aresta.congestion = round(factor, 2)


    def simular_bloqueio(self, no_origem: str, no_destino: str, bloquear: bool = True):
        """
        Bloqueia/desbloqueia uma estrada específica.
        Útil para simular acidentes ou obras.
        """
        try:
            aresta = self.grafo.get_aresta(no_origem, no_destino)
            aresta.blocked = bloquear

            # Bloqueia nos dois sentidos
            aresta_reversa = self.grafo.get_aresta(no_destino, no_origem)
            aresta_reversa.blocked = bloquear

            return True
        except ValueError:
            return False


    def obter_estado_transito(self) -> Dict:
        """Retorna snapshot do estado atual do trânsito"""
        total_arestas = sum(len(adj) for adj in self.grafo.adjacentes.values())

        # Calcula média de congestionamento
        soma_congestion = 0
        bloqueadas = 0

        for arestas in self.grafo.adjacentes.values():
            for aresta in arestas:
                soma_congestion += aresta.congestion
                if aresta.blocked:
                    bloqueadas += 1

        media_congestion = soma_congestion / total_arestas if total_arestas > 0 else 1.0

        return {
            "hora_atual": self.hora_atual,
            "factor_base": self.calcular_factor_hora(self.hora_atual),
            "congestion_media": round(media_congestion, 2),
            "estradas_bloqueadas": bloqueadas,
            "total_estradas": total_arestas // 2  # Dividido por 2 (ida e volta)
        }
