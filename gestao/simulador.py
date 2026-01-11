from __future__ import annotations
from typing import List, Optional
import random
import heapq
import time

from gestao.gestor_frota import GestorFrota
from gestao.transito_dinamico import GestorTransito
from gestao.gestor_falhas import GestorFalhas
from gestao.ride_sharing import GestorRideSharing
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
    def __init__(self, gestor: GestorFrota, duracao_total: int = 120, interface=None,
             usar_transito: bool = True, usar_falhas: bool = True, prob_falha: float = 0.15,
             usar_ride_sharing: bool = True, velocidade: int = 1):
        self.gestor = gestor
        self.duracao_total = duracao_total          # em minutos
        self.tempo_atual = 0
        self.fila_pedidos = []                      # heap de (instante, prioridade, id_pedido_atual, pedido)
        self.pedidos_todos = []                     # histórico (para métricas)
        self.interface = interface

        self.gestor_transito = GestorTransito(gestor.grafo) if usar_transito else None
        self.gestor_falhas = GestorFalhas(gestor.grafo, prob_falha) if usar_falhas else None
        self.gestor_ride_sharing = GestorRideSharing(gestor.grafo) if usar_ride_sharing else None

        # Para feedback na interface
        self.num_pedidos_pendentes_atual = 0
        self.velocidade = max(1, velocidade)


    # Adiciona um pedido que será introduzido na simulação no instante especificado.
    def agendar_pedido(self, pedido: Pedido):
        heapq.heappush(
            self.fila_pedidos, 
            (pedido.instante_pedido, -pedido.prioridade, pedido.id_pedido, pedido)) #o sinal “–” inverte a prioridade, porque a heap ordena do menor para o maior
        self.pedidos_todos.append(pedido)

    # Gera pedidos aleatórios ao longo da duração da simulação (útil para testes de stress)
    def gerar_pedidos_aleatorios(self, n: int, zonas: List[str]):
        for i in range(n):
            origem = random.choice(zonas)
            destino = random.choice([z for z in zonas if z != origem])

            pedido = Pedido(
                id_pedido=f"P{i+1}",
                posicao_inicial=origem,
                posicao_destino=destino,
                passageiros=random.randint(1, 4),
                instante_pedido=random.randint(0, self.duracao_total - 1),
                pref_ambiental=random.choice(["eletrico", "combustao"]),
                prioridade=random.randint(0, 3),
                estado=EstadoPedido.PENDENTE,
                veiculo_atribuido=None,  # <-- FIX: obrigatório no __init__ do Pedido
            )
            self.agendar_pedido(pedido)

    # Avança a simulação minuto a minuto - introduz novos pedidos agendados; tenta atribuir pedidos pendentes a veículos; executa viagens e recargas.
    def executar(self):
        print(f"Início da simulação (0 → {self.duracao_total} min)\n")

        while self.tempo_atual <= self.duracao_total:
            # Atualiza trânsito a cada minuto
            if self.gestor_transito:
                self.gestor_transito.atualizar_transito(self.tempo_atual)

            self.processar_pedidos_novos()
            self.atribuir_pedidos_pendentes()
            self.mover_veiculos()
            self.verificar_conclusao_pedidos()
            self.verificar_recargas()

            if self.tempo_atual % 5 == 0:
                self.gestor.reposicionar_veiculos(
                    self.tempo_atual,
                    [p for _, _, _, p in self.fila_pedidos]  # Pedidos futuros
                )

            if self.interface:
                self.interface.atualizar()

            self.tempo_atual += 1
            
            # Controla velocidade da simulação (interface)
            if self.interface:
                time.sleep(1.0 / self.velocidade)
            

        print("\n" + "="*60)
        print("Simulação terminada.\n")
        print("="*60)

        metricas = self.gestor.metricas.calcular_metricas()
        print("Resultados Finais:")
        for chave, valor in metricas.items():
            print(f"  {chave}: {valor}")

    # ==========================================================
    # Processamento interno
    # ==========================================================
    
    def processar_pedidos_novos(self):
        while self.fila_pedidos and self.fila_pedidos[0][0] <= self.tempo_atual:
            _, _, _, pedido = heapq.heappop(self.fila_pedidos)
            self.gestor.adicionar_pedido(pedido)
            if self.interface:
                self.interface.registar_evento(
                    f"[t={self.tempo_atual}] Pedido {pedido.id_pedido} criado "
                    f"({pedido.posicao_inicial} → {pedido.posicao_destino})"
                )



    def atribuir_pedidos_pendentes(self):
        pendentes = [p for p in self.gestor.pedidos_pendentes
                     if p.estado == EstadoPedido.PENDENTE]

        # Guarda número de pedidos pendentes para feedback na interface
        self.num_pedidos_pendentes_atual = len(pendentes)

        # Verifica pedidos expirados primeiro
        for p in pendentes:
            if p.expirou(self.tempo_atual):
                p.estado = EstadoPedido.CANCELADO
                self.gestor.metricas.pedidos_rejeitados += 1
                if self.interface:
                    tempo_espera = self.tempo_atual - p.instante_pedido
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] Pedido {p.id_pedido} CANCELADO - "
                        f"tempo máximo de espera excedido ({tempo_espera}/{p.tempo_max_espera} min)")
                continue

        # Remove pedidos cancelados da lista de pendentes
        pendentes = [p for p in pendentes if p.estado == EstadoPedido.PENDENTE]

        # SEMPRE aguarda 2 minutos antes de atribuir qualquer pedido (simula delay real de processamento)
        if len(pendentes) > 0:
            pedido_mais_antigo = min(pendentes, key=lambda p: p.instante_pedido)
            tempo_espera = self.tempo_atual - pedido_mais_antigo.instante_pedido
            if tempo_espera < 2:
                return  # Aguarda pelo menos 2 minutos antes de processar

        # Se ride sharing ativo E há apenas 1 pedido, aguarda mais tempo para acumular
        if (self.gestor_ride_sharing and
            self.interface and
            hasattr(self.interface, 'ride_sharing_ativo') and
            self.interface.ride_sharing_ativo.get() and
            len(pendentes) == 1):

            pedido_unico = pendentes[0]
            tempo_espera = self.tempo_atual - pedido_unico.instante_pedido
            if tempo_espera < 3:
                return  # Aguarda 3 minutos para possíveis agrupamentos

        # Tenta ride sharing primeiro (se ativo na interface)
        if (self.gestor_ride_sharing and
            self.interface and
            hasattr(self.interface, 'ride_sharing_ativo') and
            self.interface.ride_sharing_ativo.get() and
            len(pendentes) >= 2):

            # Procura veículos disponíveis
            veiculos_disponiveis = [v for v in self.gestor.veiculos.values()
                                   if v.estado == EstadoVeiculo.DISPONIVEL]

            for veiculo in veiculos_disponiveis:
                if len(pendentes) < 2:
                    break

                # Tenta aplicar ride sharing
                resultado = self.gestor_ride_sharing.aplicar_ride_sharing(
                    pendentes, veiculo, self.gestor
                )

                if resultado:
                    pedidos_agrupados, rota = resultado

                    # Atribui grupo ao veículo
                    veiculo.rota = rota
                    veiculo.indice_rota = 0
                    veiculo.estado = EstadoVeiculo.EM_DESLOCACAO

                    # Marca pedidos como atribuídos
                    for pedido in pedidos_agrupados:
                        pedido.estado = EstadoPedido.ATRIBUIDO
                        pedido.veiculo_atribuido = veiculo.id_veiculo
                        pendentes.remove(pedido)

                    # Log
                    if self.interface:
                        ids = ", ".join([p.id_pedido for p in pedidos_agrupados])
                        self.interface.registar_evento(
                            f"[t={self.tempo_atual}] RIDE SHARING: {veiculo.id_veiculo} -> {ids} "
                            f"({len(pedidos_agrupados)} pedidos agrupados)"
                        )

        # Ordena por prioridade (maior primeiro)
        pendentes.sort(key=lambda p: p.prioridade, reverse=True)

        # Atribui pedidos restantes individualmente
        for p in pendentes:
            veiculo = self.gestor.atribuir_pedido(p, self.tempo_atual)

            if veiculo:
                if self.interface:
                    self.interface.registar_evento(f"[t={self.tempo_atual}] Veículo {veiculo.id_veiculo} "f" atribuído ao pedido {p.id_pedido}")
                    veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
            else:
                if self.interface:
                    self.interface.registar_evento(f"[t={self.tempo_atual}] Pedido {p.id_pedido} rejeitado - "f"nenhum veículo disponível")

                if p.estado == EstadoPedido.PENDENTE:
                    p.estado = EstadoPedido.CANCELADO
                    self.gestor.metricas.pedidos_rejeitados += 1


    def mover_veiculos(self):
        """Move apenas veículos que têm rota ativa."""
        veiculos_em_movimento = [
            v for v in self.gestor.veiculos.values() 
            if v.rota and v.indice_rota < len(v.rota) - 1
        ]
    
        for v in veiculos_em_movimento:
            moveu, chegou = v.mover_um_passo(self.gestor.grafo, self.tempo_atual)
            
            if not moveu:
                continue  # Veículo ocupado ou sem rota
            
            # Atualiza métricas do movimento
            if v.indice_rota > 0:
                no_anterior = v.rota[v.indice_rota - 1]
                no_atual = v.rota[v.indice_rota]
                aresta = self.gestor.grafo.get_aresta(no_anterior, no_atual)
                
                com_passageiros = (v.estado == EstadoVeiculo.A_SERVICO)
                self.gestor.metricas.integracao_metricas(
                    v, aresta.distancia_km, com_passageiros
                )
            
            # Verifica se chegou ao destino
            if chegou:
                self.processar_chegada_destino(v)


    # Processa chegada de veículo ao destino da rota
    def processar_chegada_destino(self, veiculo: Veiculo):

        no = self.gestor.grafo.nos[veiculo.posicao]
        tipo_no = no.tipo

        # Se precisa recarregar e está numa estação apropriada E disponível
        if (veiculo.autonomia_km < 0.3 * veiculo.autonomiaMax_km and
            veiculo.pode_carregar_abastecer(tipo_no) and
            no.disponivel):

            sucesso, custo_recarga, tempo = veiculo.repor_autonomia(tipo_no, self.tempo_atual, recarga_parcial=0.8)

            if sucesso:
                # Adiciona custo de recarga às métricas
                self.gestor.metricas.custo_total += custo_recarga

            if self.interface:
                self.interface.registar_evento(
                    f"[t={self.tempo_atual}] Veículo {veiculo.id_veiculo} "f"a recarregar em {veiculo.posicao} (custo: €{custo_recarga:.2f})" )

        # Se chegou a uma estação mas ela está offline
        elif (veiculo.autonomia_km < 0.3 * veiculo.autonomiaMax_km and
              veiculo.pode_carregar_abastecer(tipo_no) and
              not no.disponivel):

            if self.interface:
                self.interface.registar_evento(
                    f"[t={self.tempo_atual}] ⚠️ Veículo {veiculo.id_veiculo} "
                    f"chegou a {veiculo.posicao} mas estação está OFFLINE!")
        
        # Se estava em deslocação sem pedido, fica disponível
        elif veiculo.estado == EstadoVeiculo.EM_DESLOCACAO:
            veiculo.estado = EstadoVeiculo.DISPONIVEL
            
            if self.interface:
                self.interface.registar_evento(
                    f"[t={self.tempo_atual}] Veículo {veiculo.id_veiculo} "f"chegou a {veiculo.posicao}")


    # Verifica se pedidos foram concluídos (veículo chegou ao destino final)
    def verificar_conclusao_pedidos(self):

        for pedido in list(self.gestor.pedidos_pendentes):
            if pedido.estado not in (EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO):
                continue
            
            veiculo = self.gestor.get_veiculo(pedido.veiculo_atribuido)
            if not veiculo:
                continue
            
            # Verifica se veículo está na posição de recolha
            if veiculo.posicao == pedido.posicao_inicial and pedido.estado == EstadoPedido.ATRIBUIDO:
                # Passou a transportar passageiros
                pedido.estado = EstadoPedido.EM_EXECUCAO
                veiculo.estado = EstadoVeiculo.A_SERVICO
                
                if self.interface:
                    self.interface.registar_evento(
                        f"[t={self.tempo_atual}] Veículo {veiculo.id_veiculo} "f"recolheu passageiros (Pedido {pedido.id_pedido})")
            
            # Verifica se chegou ao destino final
            elif (veiculo.posicao == pedido.posicao_destino and   pedido.estado == EstadoPedido.EM_EXECUCAO):
                if not veiculo.rota or veiculo.indice_rota >= len(veiculo.rota) - 1:
                    pedido.estado = EstadoPedido.CONCLUIDO
                    veiculo.estado = EstadoVeiculo.DISPONIVEL
                    veiculo.id_pedido_atual = None
                    
                    tempo_resposta = self.tempo_atual - pedido.instante_pedido
                    self.gestor.metricas.registar_pedido(pedido, tempo_resposta)
                    
                    self.gestor.pedidos_pendentes.remove(pedido)
                    self.gestor.pedidos_concluidos.append(pedido)
                    
                    if self.interface:
                        self.interface.registar_evento(
                            f"[t={self.tempo_atual}] Pedido {pedido.id_pedido} "f"concluído! (tempo: {tempo_resposta} min)")


    def verificar_recargas(self):
        for v in self.gestor.veiculos.values():
            if v.estado == EstadoVeiculo.DISPONIVEL:
                self.gestor.verificar_necessidade_recarga( v, self.tempo_atual, threshold=0.25 )

    def configurar(self, config):
        """
        Aplica configurações externas ao simulador.
        Centraliza a lógica de setup do ambiente.
        """
        # Trânsito
        if self.gestor_transito:
            self.gestor_transito.hora_inicial = config['hora_inicial']
            self.gestor_transito.hora_atual = config['hora_inicial']

        # Ride Sharing
        if self.gestor_ride_sharing and config.get('ride_sharing'):
            self.gestor_ride_sharing.raio_agrupamento = config['raio_agrupamento']
            self.gestor_ride_sharing.janela_temporal = config['janela_temporal']
