from __future__ import annotations
from typing import List, Callable, Optional
import random

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
        self.pedidos_agendados: List[Pedido] = []   # pedidos que ainda não chegaram

    # Adiciona um pedido que será introduzido na simulação no instante especificado.
    def agendar_pedido(self, pedido: Pedido):
        self.pedidos_agendados.append(pedido)

    # Gera pedidos aleatórios ao longo da duração da simulação.- instante aleatório.
    def gerar_pedidos_aleatorios(self, n: int, zonas: List[str]):
        for i in range(n):
            pedido = Pedido(
                id_pedido=f"P{i+1}",
                posicao_inicial=random.choice(zonas),
                posicao_destino=random.choice([z for z in zonas if z != zonas[0]]),
                passageiros=random.randint(1, 4),
                instante_pedido=random.randint(0, self.duracao_total - 1),
                prioridade=random.randint(0, 3),
                pref_ambiental=random.choice(["eletrico", "combustao"])
            )
            self.agendar_pedido(pedido)





    # Avança a simulação minuto a minuto - introduz novos pedidos agendados; tenta atribuir pedidos pendentes a veículos; executa viagens e recargas.
    def executar(self):
        print(f"Início da simulação (0 → {self.duracao_total} min)\n")

        for t in range(self.duracao_total + 1):
            self.tempo_atual = t
            self.processar_pedidos_novos()
            self.atribuir_pedidos_pendentes()
            self.verificar_recargas()

        print("Simulação terminada.\n")
        self.gestor.metricas.calcular_metricas()

    # ==========================================================
    # Processamento interno
    # ==========================================================
    def processar_pedidos_novos(self):
        novos = [p for p in self.pedidos_agendados 
                 if p.instante_pedido == self.tempo_atual]
        for p in novos:
            self.gestor.adicionar_pedido(p)
            print(f"[t={self.tempo_atual}] Pedido {p.id_pedido} criado ({p.posicao_inicial}→{p.posicao_destino})")
            self.pedidos_agendados.remove(p)

    def atribuir_pedidos_pendentes(self):
        pendentes = [p for p in self.gestor.pedidos_pendentes 
                     if p.estado == EstadoPedido.PENDENTE]
        for p in pendentes:
            veiculo = self.gestor.atribuir_veiculo_pedido(p)
            if veiculo:
                self.gestor.executar_viagem(veiculo, p)
                print(f"[t={self.tempo_atual}] Veiculo {veiculo.id_veiculo} atribuído ao pedido {p.id_pedido}")

    def verificar_recargas(self):
        for v in self.gestor.veiculos.values():
            if v.autonomia_km < (0.1 * v.autonomiaMax_km):
                tipo_no = self.gestor.grafo.nos[v.posicao].tipo
                if v.repor_autonomia(tipo_no):
                    print(f"[t={self.tempo_atual}] Veiculo {v.id_veiculo} recarregado na posição {v.posicao}")
