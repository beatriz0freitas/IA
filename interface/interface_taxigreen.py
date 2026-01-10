"""
Interface TaxiGreen Final
Completamente visível bem organizada.
"""

import tkinter as tk
from interface.interface_mapa import InterfaceMapa
from interface.interface_componentes import ComponentesUI, GestorPedidosVisuais
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas
import heapq


class InterfaceTaxiGreen:

    def __init__(self, simulador, config: dict):
        self.simulador = simulador
        self.config = config
        self.simulacao_ativa = False
        self.velocidade = config.get('velocidade', 1)
        self.intervalo_atualizacao = self.calcular_intervalo(self.velocidade)
        
        # Janela FIXA 1400x750
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1400x1000")
        self.root.configure(bg="#f3f4f6")
        self.root.resizable(False, False)
        
        self.gestor_pedidos_visuais = None
        
        self.criar_interface()
        self.root.after(self.intervalo_atualizacao, self.atualizar)

    def calcular_intervalo(self, velocidade):
        """Calcula intervalo."""
        intervalos = {1: 1000, 2: 500, 5: 200, 10: 100}
        return intervalos.get(velocidade, 1000)

    def criar_interface(self):
        """Cria interface."""
        
        # MAPA (65%)
        frame_mapa = tk.Frame(self.root, bg="#f3f4f6")
        frame_mapa.pack(side="left", fill="both", expand=True, padx=(6, 3), pady=6)
        
        self.mapa = InterfaceMapa(
            frame_mapa, 
            self.simulador.gestor.grafo, 
            width=900, height=738
        )

        # SIDEBAR (35%) - SEM SCROLL
        frame_sidebar = tk.Frame(self.root, bg="#ffffff", width=488)
        frame_sidebar.pack(side="right", fill="both", padx=(3, 6), pady=6)
        frame_sidebar.pack_propagate(False)

        # COMPONENTES
        componentes = ComponentesUI(frame_sidebar, self.config)
        
        # 1. Header
        widgets_header = componentes.criar_header(frame_sidebar)
        self.label_tempo = widgets_header['label_tempo']
        self.label_hora = widgets_header['label_hora']
        self.label_transito = widgets_header['label_transito']
        
        # 2. Configuração
        componentes.criar_info_config(frame_sidebar, len(self.simulador.fila_pedidos))
        
        # 3. Frota
        cards_frota = componentes.criar_frota_compacta(frame_sidebar)
        self.card_disponiveis = cards_frota['disponiveis']
        self.card_servico = cards_frota['servico']
        self.card_recarga = cards_frota['recarga']
        self.card_indisp = cards_frota['indisp']
        
        # 4. Pedidos
        widgets_pedidos = componentes.criar_pedidos_lista(frame_sidebar)
        self.gestor_pedidos_visuais = GestorPedidosVisuais(
            widgets_pedidos['container'],
            widgets_pedidos['canvas'],
            widgets_pedidos['label_contador'],
            componentes
        )
        
        # 5. Métricas
        self.metricas_labels = componentes.criar_metricas_completas(frame_sidebar)
        
        # 6. Log
        self.text_log = componentes.criar_log(frame_sidebar)

        # 7. Botões
        botoes = componentes.criar_botoes(frame_sidebar)
        self.btn_iniciar = botoes['btn_iniciar']
        self.btn_pausar = botoes['btn_pausar']
        
        self.btn_iniciar.config(command=self.executar_simulacao)
        self.btn_pausar.config(command=self.pausar_simulacao)

    def registar_evento(self, msg: str):
        """Log."""
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def atualizar(self):
        """Atualiza interface."""
        m = self.simulador.gestor.metricas
        metrics = m.calcular_metricas()

        # TEMPO
        self.label_tempo.config(
            text=f"{self.simulador.tempo_atual}/{self.config['duracao']} min"
        )

        # HORA/TRANSITO
        if self.simulador.gestor_transito:
            hora = self.simulador.gestor_transito.hora_atual
            self.label_hora.config(text=f"Hora: {hora:02d}:00")

            factor = self.simulador.gestor_transito.calcular_factor_hora(hora)
            if factor >= 1.8:
                self.label_transito.config(text="Transito: RUSH!", fg="#ef4444")
            elif factor >= 1.3:
                self.label_transito.config(text="Transito: Moderado", fg="#f59e0b")
            elif factor < 1.0:
                self.label_transito.config(text="Transito: Fluido", fg="#10b981")
            else:
                self.label_transito.config(text="Transito: Normal", fg="#6b7280")

        # FROTA
        veiculos = self.simulador.gestor.veiculos.values()
        total = len(veiculos)
        
        disponiveis = sum(1 for v in veiculos if v.estado == EstadoVeiculo.DISPONIVEL)
        servico = sum(1 for v in veiculos if v.estado in (EstadoVeiculo.EM_DESLOCACAO, EstadoVeiculo.A_SERVICO))
        recarga = sum(1 for v in veiculos if v.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER))
        indisp = sum(1 for v in veiculos if v.estado == EstadoVeiculo.INDISPONIVEL)

        self.card_disponiveis.config(text=f"{disponiveis}/{total}")
        self.card_servico.config(text=str(servico))
        self.card_recarga.config(text=str(recarga))
        self.card_indisp.config(text=str(indisp))

        # PEDIDOS
        pedidos_ativos = [
            p for p in self.simulador.gestor.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)
        ]
        self.gestor_pedidos_visuais.atualizar(pedidos_ativos)

        # METRICAS
        total_pedidos = metrics['pedidos_servicos'] + metrics['pedidos_rejeitados']
        self.metricas_labels["pedidos"].config(text=f"{metrics['pedidos_servicos']}/{total_pedidos}")
        self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
        self.metricas_labels["tempo_resp"].config(text=f"{metrics['tempo_medio_resposta']:.1f}m")
        self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
        self.metricas_labels["dead_mileage"].config(text=f"{metrics['perc_km_vazio']:.1f}%")
        self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")
        self.metricas_labels["emissoes"].config(text=f"{metrics['emissoes_totais']:.1f}kg")

        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            total_est = estado['estacoes_recarga']['total'] + estado['postos_abastecimento']['total']
            online_est = estado['estacoes_recarga']['online'] + estado['postos_abastecimento']['online']
            self.metricas_labels["estacoes"].config(text=f"{online_est}/{total_est}")

        if "ride_sharing" in self.metricas_labels and self.simulador.gestor_ride_sharing:
            stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
            self.metricas_labels["ride_sharing"].config(text=str(stats['grupos_criados']))

        # MAPA
        estacoes_offline = set()
        if self.simulador.gestor_falhas:
            todas = (
                self.simulador.gestor_falhas.obter_estacoes_recarga() +
                self.simulador.gestor_falhas.obter_postos_abastecimento()
            )
            for est_id in todas:
                no = self.simulador.gestor.grafo.nos[est_id]
                if not no.disponivel:
                    estacoes_offline.add(est_id)
            self.mapa.desenhar_nos(estacoes_offline)

        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos_ativos)

        try:
            self.root.after(self.intervalo_atualizacao, self.atualizar)
        except tk.TclError:
            pass

    def executar_simulacao(self):
        """Inicia."""
        if self.simulador.tempo_atual >= self.config['duracao']:
            self.reiniciar_simulacao()

        self.simulacao_ativa = True
        self.registar_evento(f"Simulacao iniciada ({self.velocidade}x)")
        self.executar_passo()

    def executar_passo(self):
        """Executa passos."""
        if not self.simulacao_ativa or self.simulador.tempo_atual > self.config['duracao']:
            if self.simulador.tempo_atual > self.config['duracao']:
                self.finalizar_simulacao()
            return

        passos = self.velocidade
        for _ in range(passos):
            if self.simulador.tempo_atual > self.config['duracao']:
                break
            self.executar_passo_individual()

    def executar_passo_individual(self):
        """Um minuto."""
        if self.simulador.gestor_transito:
            self.simulador.gestor_transito.atualizar_transito(self.simulador.tempo_atual)

        if self.simulador.gestor_falhas and self.simulador.tempo_atual % 5 == 0:
            falhas = self.simulador.gestor_falhas.simular_falha_aleatoria(self.simulador.tempo_atual)
            for est_id in falhas:
                self.registar_evento(f"[t={self.simulador.tempo_atual}] {est_id} OFFLINE")

        self.simulador.processar_pedidos_novos()
        self.simulador.atribuir_pedidos_pendentes()
        self.simulador.mover_veiculos()
        self.simulador.verificar_conclusao_pedidos()
        self.simulador.verificar_recargas()

        if self.simulador.tempo_atual % 5 == 0 and self.config.get('reposicionamento', False):
            pedidos_futuros = [p for _, _, _, p in self.simulador.fila_pedidos]
            self.simulador.gestor.reposicionar_veiculos(
                self.simulador.tempo_atual, pedidos_futuros
            )

        self.simulador.tempo_atual += 1
        self.root.after(self.intervalo_atualizacao, self.executar_passo)

    def pausar_simulacao(self):
        """Pausa/retoma."""
        if self.simulacao_ativa:
            self.simulacao_ativa = False
            self.btn_pausar.config(text="Retomar", bg="#10b981")
            self.registar_evento("PAUSADA")
        else:
            self.simulacao_ativa = True
            self.btn_pausar.config(text="Pausar", bg="#ef4444")
            self.registar_evento("RETOMADA")
            self.executar_passo()

    def finalizar_simulacao(self):
        """Finaliza."""
        self.simulacao_ativa = False
        metricas = self.simulador.gestor.metricas.calcular_metricas()

        self.registar_evento("\n" + "="*40)
        self.registar_evento(" SIMULACAO CONCLUIDA")
        self.registar_evento("="*40)
        self.registar_evento(f"Servidos: {metricas['pedidos_servicos']}")
        self.registar_evento(f"Rejeitados: {metricas['pedidos_rejeitados']}")
        self.registar_evento(f"Taxa: {metricas['taxa_sucesso']}%")
        
        self.mostrar_popup_resultados(metricas)

    def mostrar_popup_resultados(self, metricas):
        """Popup resultados."""
        popup = tk.Toplevel(self.root)
        popup.title("Simulacao Concluida")
        popup.geometry("480x550")
        popup.configure(bg="#ffffff")
        popup.transient(self.root)
        popup.resizable(False, False)

        # Header
        tk.Frame(popup, bg="#10b981", height=60).pack(fill="x")
        tk.Label(
            popup, text="Simulacao Concluida",
            bg="#10b981", fg="#ffffff",
            font=("Inter", 15, "bold")
        ).place(x=240, y=20, anchor="center")

        # Conteúdo
        content = tk.Frame(popup, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        resultados = [
            ("Pedidos Atendidos", f"{metricas['pedidos_servicos']}/{metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']}"),
            ("Taxa de Sucesso", f"{metricas['taxa_sucesso']:.1f}%"),
            ("Tempo Medio", f"{metricas['tempo_medio_resposta']:.1f} min"),
            ("Custo Total", f"€{metricas['custo_total']:.2f}"),
            ("Emissoes CO2", f"{metricas['emissoes_totais']:.1f} kg"),
            ("Km Totais", f"{metricas['km_totais']:.1f} km"),
            ("Dead Mileage", f"{metricas['perc_km_vazio']:.1f}%"),
        ]

        for label, valor in resultados:
            row = tk.Frame(content, bg="#ffffff")
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=label + ":",
                bg="#ffffff", fg="#6b7280",
                font=("Inter", 9)
            ).pack(side="left")
            tk.Label(
                row, text=valor,
                bg="#ffffff", fg="#111827",
                font=("Inter", 9, "bold")
            ).pack(side="right")

        tk.Button(
            popup, text="Fechar",
            command=popup.destroy,
            bg="#3b82f6", fg="#ffffff",
            font=("Inter", 9, "bold"),
            relief="flat", padx=30, pady=8,
            cursor="hand2"
        ).pack(pady=15)

    def reiniciar_simulacao(self):
        """Reinicia."""
        self.simulador.tempo_atual = 0
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []
        
        self.simulador.fila_pedidos = []
        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(
                self.simulador.fila_pedidos, 
                (pedido.instante_pedido, -pedido.prioridade, pedido.id_pedido, pedido)
            )
        
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0
        
        self.simulador.gestor.metricas = Metricas()
        self.gestor_pedidos_visuais.limpar()
        self.registar_evento("Simulacao reiniciada")

    def iniciar(self):
        """Inicia loop."""
        self.root.mainloop()