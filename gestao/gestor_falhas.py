"""
Sistema de gestão de falhas em estações e postos.
Simula estações de recarga e postos de abastecimento fora de serviço.
"""

import random
from typing import List, Dict
from modelo.grafo import Grafo, TipoNo


class GestorFalhas:
    """
    Gere falhas aleatórias em estações de recarga e postos de abastecimento.

    Tipos de falhas:
    - Estações de recarga: podem ficar offline (falha técnica, manutenção)
    - Postos de abastecimento: podem ficar sem combustível
    """

    def __init__(self, grafo: Grafo, prob_falha: float = 0.05):
        """
        Args:
            grafo: Grafo da cidade
            prob_falha: Probabilidade de falha por estação a cada verificação (padrão 5%)
        """
        self.grafo = grafo
        self.prob_falha = prob_falha
        self.historico_falhas: List[Dict] = []


    def obter_estacoes_recarga(self) -> List[str]:
        """Retorna lista de IDs de estações de recarga"""
        return [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo == TipoNo.ESTACAO_RECARGA
        ]


    def obter_postos_abastecimento(self) -> List[str]:
        """Retorna lista de IDs de postos de abastecimento"""
        return [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo == TipoNo.POSTO_ABASTECIMENTO
        ]


    def simular_falha_aleatoria(self, tempo_atual: int) -> List[str]:
        """
        Simula falhas aleatórias em estações/postos.

        Returns:
            Lista de IDs de estações que falharam neste instante
        """
        estacoes = self.obter_estacoes_recarga()
        postos = self.obter_postos_abastecimento()
        todas_estacoes = estacoes + postos

        falhas_novas = []

        for est_id in todas_estacoes:
            no = self.grafo.nos[est_id]

            # Se já está offline, pode voltar online (50% de chance)
            if not no.disponivel:
                if random.random() < 0.5:
                    no.disponivel = True
                    self.historico_falhas.append({
                        "tempo": tempo_atual,
                        "estacao": est_id,
                        "tipo": "RECUPERACAO"
                    })
            # Se está online, pode falhar
            elif random.random() < self.prob_falha:
                no.disponivel = False
                falhas_novas.append(est_id)
                self.historico_falhas.append({
                    "tempo": tempo_atual,
                    "estacao": est_id,
                    "tipo": "FALHA"
                })

        return falhas_novas


    def forcar_falha(self, estacao_id: str, tempo_atual: int) -> bool:
        """
        Força uma estação específica a falhar.

        Returns:
            True se conseguiu forçar falha, False se estação não existe
        """
        if estacao_id not in self.grafo.nos:
            return False

        no = self.grafo.nos[estacao_id]
        no.disponivel = False

        self.historico_falhas.append({
            "tempo": tempo_atual,
            "estacao": estacao_id,
            "tipo": "FALHA_FORCADA"
        })

        return True


    def recuperar_estacao(self, estacao_id: str, tempo_atual: int) -> bool:
        """
        Recupera uma estação que estava offline.

        Returns:
            True se conseguiu recuperar, False se estação não existe
        """
        if estacao_id not in self.grafo.nos:
            return False

        no = self.grafo.nos[estacao_id]
        no.disponivel = True

        self.historico_falhas.append({
            "tempo": tempo_atual,
            "estacao": estacao_id,
            "tipo": "RECUPERACAO_MANUAL"
        })

        return True


    def obter_estacoes_disponiveis(self, tipo: TipoNo) -> List[str]:
        """
        Retorna estações disponíveis de um tipo específico.

        Args:
            tipo: TipoNo.ESTACAO_RECARGA ou TipoNo.POSTO_ABASTECIMENTO

        Returns:
            Lista de IDs de estações disponíveis
        """
        return [
            no_id for no_id, no in self.grafo.nos.items()
            if no.tipo == tipo and no.disponivel
        ]


    def obter_estado_estacoes(self) -> Dict:
        """Retorna estado atual de todas as estações"""
        estacoes = self.obter_estacoes_recarga()
        postos = self.obter_postos_abastecimento()

        estacoes_online = sum(1 for e in estacoes if self.grafo.nos[e].disponivel)
        postos_online = sum(1 for p in postos if self.grafo.nos[p].disponivel)

        return {
            "estacoes_recarga": {
                "total": len(estacoes),
                "online": estacoes_online,
                "offline": len(estacoes) - estacoes_online,
                "taxa_disponibilidade": round(estacoes_online / len(estacoes) * 100, 1) if estacoes else 0
            },
            "postos_abastecimento": {
                "total": len(postos),
                "online": postos_online,
                "offline": len(postos) - postos_online,
                "taxa_disponibilidade": round(postos_online / len(postos) * 100, 1) if postos else 0
            },
            "total_falhas_historico": len(self.historico_falhas)
        }


    def limpar_historico(self):
        """Limpa histórico de falhas"""
        self.historico_falhas = []
