"""
Simulador refatorizado - Controla fluxo temporal da simulação
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import heapq

from gestao.gestor_frota import GestorFrota
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido

# TYPE_CHECKING evita import cíclico
if TYPE_CHECKING:
    from interface_taxigreen import InterfaceTaxiGreen


class Simulador:
    """
    Responsável por gerir o tempo e os eventos dinâmicos da simulação:
    - Chegada de pedidos no tempo correto
    - Atribuição de veículos disponíveis
    - Execução de viagens (movimentação passo a passo)
    - Recarga automática de veículos com autonomia baixa
    """

    def __init__(self, gestor: GestorFrota, duracao_total: int = 120):
        self.gestor = gestor
        self.duracao_total = duracao_total  # em minutos
        self.tempo_atual = 0
        self.fila_pedidos = []  # heap de (instante, prioridade, pedido)
        self.pedidos_todos = []  # histórico completo
        self.interface: Optional[InterfaceTaxiGreen] = None
        self.em_execucao = False

    def set_interface(self, interface: InterfaceTaxiGreen):
        """Define interface sem criar ciclo de imports"""
        self.interface = interface

    def agendar_pedido(self, pedido: Pedido):
        """Adiciona um pedido à fila de espera da simulação"""
        heapq.heappush(
            self.fila_pedidos,
            (pedido.instante_pedido, -pedido.prioridade, pedido)
        )
        self.pedidos_todos.append(pedido)

    def gerar_pedidos_aleatorios(self, n: int, zonas: List[str]):
        """Gera n pedidos aleatórios ao longo da simulação"""
        import random
        for i in range(n):
            pedido = Pedido(
                id_pedido=f"P{i+1}",
                posicao_inicial=random.choice(zonas),
                posicao_destino=random.choice(
                    [z for z in zonas if z != zonas[0]]
                ),
                passageiros=random.randint(1, 4),
                instante_pedido=random.randint(0, self.duracao_total - 1),
                pref_ambiental=random.choice(["eletrico", "combustao"]),
                prioridade=random.randint(0, 3),
                estado=EstadoPedido.PENDENTE
            )
            self.agendar_pedido(pedido)

    def executar(self):
        """Loop principal da simulação - avança minuto a minuto"""
        print(f"\n▶ Simulação iniciada (0 → {self.duracao_total} min)\n")
        self.em_execucao = True
        self.tempo_atual = 0

        while self.tempo_atual <= self.duracao_total and self.em_execucao:
            # 1. Processar novos pedidos chegados
            self._processar_pedidos_novos()

            # 2. Atribuir pedidos pendentes a veículos disponíveis
            self._atribuir_pedidos_pendentes()

            # 3. Mover todos os veículos um passo
            self._mover_veiculos()

            # 4. Verificar recargas necessárias
            self._verificar_recargas()

            # 5. Atualizar interface
            if self.interface:
                self.interface.atualizar_renderizacao()

            self.tempo_atual += 1

        print(f"\n✓ Simulação terminada")
        if self.interface:
            self.interface.registar_evento("Simulação concluída")

    def pausar(self):
        """Para a execução da simulação"""
        self.em_execucao = False

    # ==================== MÉTODOS INTERNOS ====================

    def _processar_pedidos_novos(self):
        """Remove pedidos da fila que chegam no tempo_atual"""
        while (self.fila_pedidos and
               self.fila_pedidos[0][0] == self.tempo_atual):
            _, _, pedido = heapq.heappop(self.fila_pedidos)

            # Validar pedido
            if not self._validar_pedido(pedido):
                pedido.estado = EstadoPedido.REJEITADO
                if self.interface:
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] ✗ Pedido {pedido.id_pedido} "
                        f"rejeitado (origem/destino inválido)"
                    )
                continue

            self.gestor.adicionar_pedido(pedido)

            if self.interface:
                self.interface.registar_evento(
                    f"[t={self.tempo_atual}] + Pedido {pedido.id_pedido}: "
                    f"{pedido.posicao_inicial} → {pedido.posicao_destino}"
                )
                self.interface.mostrar_pedido(pedido)

    def _atribuir_pedidos_pendentes(self):
        """Tenta atribuir cada pedido PENDENTE a um veículo disponível"""
        pendentes = [
            p for p in self.gestor.pedidos_pendentes
            if p.estado == EstadoPedido.PENDENTE
        ]

        for pedido in pendentes:
            veiculo = self.gestor.atribuir_pedido(pedido)
            if veiculo:
                if self.interface:
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] ↳ {veiculo.id_veiculo} "
                        f"atribuído a {pedido.id_pedido}"
                    )
            else:
                if self.interface:
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] ⚠ Pedido {pedido.id_pedido} "
                        f"sem veículo disponível"
                    )

    def _mover_veiculos(self):
        """Move cada veículo um passo na sua rota (se tiver)"""
        for v in self.gestor.veiculos.values():
            if not v.rota:
                continue  # Sem rota atribuída

            em_movimento = v.mover_um_passo(self.gestor.grafo)

            if em_movimento:
                # Calcular distância do último movimento
                no_anterior = (
                    v.rota[v.indice_rota - 1]
                    if v.indice_rota > 0
                    else v.posicao
                )
                no_atual = v.rota[v.indice_rota]
                aresta = self.gestor.grafo.get_aresta(no_anterior, no_atual)

                # Integrar métricas
                self.gestor.metricas.integracao_metricas(v, aresta.distancia_km)

                if self.interface:
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] → {v.id_veiculo} "
                        f"em rota (pos: {v.posicao})"
                    )

            # Se rota terminou
            if not em_movimento and v.rota:
                pedido_ativo = self._encontrar_pedido_veiculo(v.id_veiculo)

                if pedido_ativo and pedido_ativo.estado == EstadoPedido.ATRIBUIDO:
                    # Concluir pedido
                    pedido_ativo.estado = EstadoPedido.CONCLUIDO
                    tempo_resposta = self.tempo_atual - pedido_ativo.instante_pedido
                    self.gestor.metricas.registar_pedido(
                        pedido_ativo, tempo_resposta
                    )

                    if self.interface:
                        self.interface.registar_evento(
                            f"[t={self.tempo_atual}] ✓ Pedido "
                            f"{pedido_ativo.id_pedido} concluído"
                        )
                        self.interface.remover_pedido_visual(pedido_ativo)

                    # Remover de pendentes
                    if pedido_ativo in self.gestor.pedidos_pendentes:
                        self.gestor.pedidos_pendentes.remove(pedido_ativo)
                    self.gestor.pedidos_concluidos.append(pedido_ativo)

                # Limpar rota do veículo
                v.rota = []
                v.indice_rota = 0
                v.estado = EstadoVeiculo.DISPONIVEL

    def _verificar_recargas(self):
        """Recarrega veículos com autonomia baixa (<10%)"""
        for v in self.gestor.veiculos.values():
            limiar = 0.1 * v.autonomiaMax_km

            if v.autonomia_km < limiar and v.posicao:
                tipo_no = self.gestor.grafo.nos[v.posicao].tipo
                sucesso = v.repor_autonomia(tipo_no)

                if sucesso:
                    if self.interface:
                        self.interface.registar_evento(
                            f"[t={self.tempo_atual}] ⚡ {v.id_veiculo} "
                            f"recarregado em {v.posicao}"
                        )

    # ==================== MÉTODOS AUXILIARES ====================

    def _validar_pedido(self, pedido: Pedido) -> bool:
        """Verifica se origem e destino existem no grafo"""
        return (
            pedido.posicao_inicial in self.gestor.grafo.nos and
            pedido.posicao_destino in self.gestor.grafo.nos and
            pedido.posicao_inicial != pedido.posicao_destino and
            pedido.passageiros > 0
        )

    def _encontrar_pedido_veiculo(self, id_veiculo: str) -> Optional[Pedido]:
        """Encontra o pedido atribuído a um veículo"""
        for p in self.gestor.pedidos_pendentes:
            if p.veiculo_atribuido == id_veiculo:
                return p
        return None