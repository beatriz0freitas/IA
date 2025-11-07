from __future__ import annotations
from typing import List, Callable, Optional
import random
import heapq

from gestao.gestor_frota import GestorFrota
from modelo.veiculos import Veiculo, EstadoVeiculo
from modelo.pedidos import Pedido, EstadoPedido
from interface_taxigreen import InterfaceTaxiGreen

"""
Responsável por gerir o tempo e os eventos dinâmicos da simulação.
      - chegada de pedidos no tempo correto;
      - atribuição de veículos disponíveis;
      - execução de viagens;
      - recarga automática de veículos com autonomia baixa.
"""
class Simulador:
    #todo: nao gosto de duracao já ter um valor fixo
    def __init__(self, gestor: GestorFrota, duracao_total: int = 120, interface=None):
        self.gestor = gestor
        self.duracao_total = duracao_total          # em minutos
        self.tempo_atual = 0
        self.fila_pedidos = []                      # heap de (instante, prioridade, pedido)
        self.pedidos_todos = []                     # histórico (para métricas)
        self.interface = interface


    # Adiciona um pedido que será introduzido na simulação no instante especificado.
    def agendar_pedido(self, pedido: Pedido):
        heapq.heappush(self.fila_pedidos, 
                       (pedido.instante_pedido, -pedido.prioridade, pedido)) #o sinal “–” inverte a prioridade, porque a heap ordena do menor para o maior
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
            
            if self.interface:
                self.interface.atualizar()
            
            self.tempo_atual += 1

        print("Simulação terminada.\n")
        self.gestor.metricas.calcular_metricas()

    # ==========================================================
    # Processamento interno
    # ==========================================================
    
    def processar_pedidos_novos(self):
        while self.fila_pedidos and self.fila_pedidos[0][0] == self.tempo_atual:
            #pedido é removido da heap para nao ser processado again
            _, _, pedido = heapq.heappop(self.fila_pedidos)

            self.gestor.adicionar_pedido(pedido)
            if hasattr(self, "interface") and self.interface:
                self.interface.registar_evento(f"[t={self.tempo_atual}] Pedido {pedido.id_pedido} criado ({pedido.posicao_inicial} → {pedido.posicao_destino})")
                self.interface.mostrar_pedido(pedido)

    def atribuir_pedidos_pendentes(self):
        pendentes = [p for p in self.gestor.pedidos_pendentes if p.estado == EstadoPedido.PENDENTE]
        for p in pendentes:
            veiculo = self.gestor.atribuir_pedido(p)
            if veiculo:
                print(f"[t={self.tempo_atual}] Veículo {veiculo.id_veiculo} atribuído ao pedido {p.id_pedido}")
                veiculo.estado = EstadoVeiculo.EM_DESLOCACAO

    def mover_veiculos(self):
        for v in self.gestor.veiculos.values():
            if not v.rota:
                continue  # sem rota atribuída

            # tenta mover um passo
            em_movimento = v.mover_um_passo(self.gestor.grafo)
            if em_movimento:
                no_anterior = v.rota[v.indice_rota - 1] if v.indice_rota > 0 else v.posicao
                no_atual = v.rota[v.indice_rota]
                distancia = self.gestor.grafo.get_aresta(no_anterior, no_atual).distancia_km
                self.gestor.metricas.integracao_metricas(v, distancia)
            
            if hasattr(self, "interface") and self.interface:
                self.interface.registar_evento(f"[t={self.tempo_atual}] Veículo {v.id_veiculo} moveu-se para {v.posicao} (rota {v.id_rota})")

            if not em_movimento and v.estado == EstadoVeiculo.DISPONIVEL:
                print(f"[t={self.tempo_atual}] Veículo {v.id_veiculo} concluiu rota {v.id_rota}.")

            # atualizar a interface 
            if hasattr(self, "interface") and self.interface is not None:
                self.interface.atualizar()

    def verificar_recargas(self):
        for v in self.gestor.veiculos.values():
            if v.autonomia_km < (0.1 * v.autonomiaMax_km):
                tipo_no = self.gestor.grafo.nos[v.posicao].tipo
                if v.repor_autonomia(tipo_no):
                    v.estado = EstadoVeiculo.DISPONIVEL
                    print(f"[t={self.tempo_atual}] Veiculo {v.id_veiculo} recarregado na posição {v.posicao}")
