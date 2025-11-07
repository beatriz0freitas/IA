from __future__ import annotations
from typing import List, Callable, Optional
import random
import heapq

from gestao.gestor_frota import GestorFrota
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido

"""
Responsável por gerir o tempo e os eventos dinâmicos da simulação.
      - chegada de pedidos no tempo correto;
      - atribuição de veículos disponíveis;
      - execução de viagens;
      - recarga automática de veículos com autonomia baixa.
"""
class Simulador:
    def __init__(self, gestor: GestorFrota, duracao_total: int = 120):
        self.gestor = gestor
        self.duracao_total = duracao_total          # em minutos
        self.tempo_atual = 0
        self.fila_pedidos = []                      # heap de (instante, prioridade, pedido)
        self.pedidos_todos = []                     # histórico (para métricas)

    # Adiciona um pedido que será introduzido na simulação no instante especificado.
    def agendar_pedido(self, pedido: Pedido):
        heapq.heappush(self.fila_pedidos, (pedido.instante_pedido, -pedido.prioridade, pedido))
        self.pedidos_todos.append(pedido)

    # Gera pedidos aleatórios ao longo da duração da simulação.- instante aleatório.
    def gerar_pedidos_aleatorios(self, n: int, zonas: List[str]):
        for i in range(n):
            pedido = Pedido(
                id_pedido=f"P{i+1}",
                posicao_inicial=random.choice(zonas),
                posicao_destino=random.choice([z for z in zonas if z != zonas[0]]),
                passageiros=random.randint(1, 4),
                instante_pedido=random.randint(0, self.duracao_total - 1),
                pref_ambiental=random.choice(["eletrico", "combustao"]),
                prioridade=random.randint(0, 3),
                estado=EstadoPedido.PENDENTE
            )
            self.agendar_pedido(pedido)



    # Avança a simulação minuto a minuto - introduz novos pedidos agendados; tenta atribuir pedidos pendentes a veículos; executa viagens e recargas.
    def executar(self):
        print(f"Início da simulação (0 → {self.duracao_total} min)\n")

        while self.tempo_atual <= self.duracao_total:
            self.processar_pedidos_novos()
            self.atribuir_pedidos_pendentes()
            self.mover_veiculos()
            self.verificar_recargas()
            self.tempo_atual += 1

        print("Simulação terminada.\n")
        self.gestor.metricas.calcular_metricas()

    # ==========================================================
    # Processamento interno
    # ==========================================================
    def processar_pedidos_novos(self):
        while self.fila_pedidos and self.fila_pedidos[0][0] == self.tempo_atual:
            _, _, pedido = heapq.heappop(self.fila_pedidos)
            self.gestor.adicionar_pedido(pedido)
            print(f"[t={self.tempo_atual}] Pedido {pedido.id_pedido} criado ({pedido.posicao_inicial}→{pedido.posicao_destino})")

    def mover_veiculos(self):
        for v in self.gestor.veiculos.values():
            if hasattr(v, "rota"):
                chegou = not v.mover_um_passo(self.gestor.grafo)
                if chegou:
                    v.estado = EstadoVeiculo.DISPONIVEL

    def atribuir_pedidos_pendentes(self):
        pendentes = [p for p in self.gestor.pedidos_pendentes 
                     if p.estado == EstadoPedido.PENDENTE]
        for p in pendentes:
            veiculo = self.gestor.atribuir_pedido(p)
            if veiculo:
                self.gestor.executar_viagem(veiculo, p, self.tempo_atual)
                print(f"[t={self.tempo_atual}] Veiculo {veiculo.id_veiculo} atribuído ao pedido {p.id_pedido}")

    def verificar_recargas(self):
        for v in self.gestor.veiculos.values():
            if v.autonomia_km < (0.1 * v.autonomiaMax_km):
                tipo_no = self.gestor.grafo.nos[v.posicao].tipo
                if v.repor_autonomia(tipo_no):
                    v.estado = EstadoVeiculo.DISPONIVEL
                    print(f"[t={self.tempo_atual}] Veiculo {v.id_veiculo} recarregado na posição {v.posicao}")
