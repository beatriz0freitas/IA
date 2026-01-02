import tkinter as tk
from tkinter import ttk
import heapq
from interface_mapa import InterfaceMapa
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas

class InterfaceTaxiGreen:

    def __init__(self, simulador):
        self.simulador = simulador
        self.simulacao_ativa = False
        self.simulacao_pausada = False
        self.velocidade = 1  # 1x, 2x, 5x
        self.intervalo_atualizacao = 1000  # ms
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f9fafb")
        self.root.minsize(1200, 700)
        self.simulacao_ativa = False

        self.criar_layout_principal()
        self.root.after(self.intervalo_atualizacao, self.atualizar)

    def criar_layout_principal(self):

        # ===== MAPA =====
        self.frame_mapa = tk.Frame(self.root, bg="#f9fafb")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo, width=900, height=700)

        # ===== SIDEBAR =====
        self.frame_direita = tk.Frame(self.root, bg="#ffffff", width=380)
        self.frame_direita.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.frame_direita.pack_propagate(False)

        # Container com scroll para conteúdo
        self.canvas_scroll = tk.Canvas(self.frame_direita, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame_direita, orient="vertical", command=self.canvas_scroll.yview)
        self.frame_conteudo = tk.Frame(self.canvas_scroll, bg="#ffffff")

        self.frame_conteudo.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )

        self.canvas_scroll.create_window((0, 0), window=self.frame_conteudo, anchor="nw")
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        self.criar_header()
        self.criar_secao_hora_inicial()
        self.criar_secao_algoritmo()
        self.criar_secao_frota()
        self.criar_secao_metricas()
        self.criar_secao_pedidos()
        self.criar_secao_eventos()

        # Botões fixos no fundo (fora do scroll)
        self.frame_botoes_fixo = tk.Frame(self.frame_direita, bg="#ffffff")
        self.frame_botoes_fixo.pack(side="bottom", fill="x", before=self.canvas_scroll)

        self.criar_botoes()

    def criar_header(self):
        header = tk.Frame(self.frame_conteudo, bg="#ffffff")
        header.pack(fill="x", padx=20, pady=15)

        tk.Label(header, text="TaxiGreen",
                bg="#ffffff", fg="#111827",
                font=("Inter", 18, "bold")).pack(anchor="w")

        self.label_tempo = tk.Label(header, text="Tempo: 0/60 min",
                                   bg="#ffffff", fg="#6b7280",
                                   font=("Inter", 11))
        self.label_tempo.pack(anchor="w", pady=(2, 0))

        # Trânsito e Hora
        info_frame = tk.Frame(header, bg="#ffffff")
        info_frame.pack(anchor="w", pady=(4, 0))

        self.label_hora = tk.Label(info_frame, text="Hora: 00:00",
                                   bg="#ffffff", fg="#6b7280",
                                   font=("Helvetica", 10))
        self.label_hora.pack(side="left", padx=(0, 10))

        self.label_transito = tk.Label(info_frame, text="Transito: Normal",
                                      bg="#ffffff", fg="#10b981",
                                      font=("Helvetica", 10, "bold"))
        self.label_transito.pack(side="left")

        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 15))

    def criar_secao_hora_inicial(self):
        """Seção para escolher hora inicial"""
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(frame, text="Hora Inicial",
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))

        # Frame para opções
        opcoes_frame = tk.Frame(frame, bg="#f9fafb", relief="flat")
        opcoes_frame.pack(fill="x", pady=5)

        self.hora_inicial_var = tk.StringVar(value="aleatoria")

        # Opção: Aleatória
        rb_aleatorio = tk.Radiobutton(
            opcoes_frame,
            text="Aleatória (0-23h)",
            variable=self.hora_inicial_var,
            value="aleatoria",
            bg="#f9fafb",
            fg="#374151",
            font=("Inter", 10),
            selectcolor="#f9fafb",
            activebackground="#f9fafb",
            command=self.atualizar_hora_inicial
        )
        rb_aleatorio.pack(anchor="w", padx=10, pady=3)

        # Opção: Escolher
        escolher_frame = tk.Frame(opcoes_frame, bg="#f9fafb")
        escolher_frame.pack(anchor="w", padx=10, pady=3)

        rb_escolher = tk.Radiobutton(
            escolher_frame,
            text="Escolher:",
            variable=self.hora_inicial_var,
            value="escolhida",
            bg="#f9fafb",
            fg="#374151",
            font=("Inter", 10),
            selectcolor="#f9fafb",
            activebackground="#f9fafb",
            command=self.atualizar_hora_inicial
        )
        rb_escolher.pack(side="left")

        # Spinbox para escolher hora (0-23)
        self.hora_escolhida = tk.Spinbox(
            escolher_frame,
            from_=0,
            to=23,
            width=5,
            font=("Inter", 10),
            bg="#ffffff",
            fg="#374151",
            state="disabled"
        )
        self.hora_escolhida.pack(side="left", padx=5)

        tk.Label(escolher_frame, text="h",
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 10)).pack(side="left")

        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 15))

    def criar_secao_algoritmo(self):
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(frame, text="Algoritmo de Procura",
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))

        self.algoritmo_var = tk.StringVar(value="astar")
        self.reposicionamento_ativo = tk.BooleanVar(value=True)  # Reposicionamento ativo por padrão
        self.ride_sharing_ativo = tk.BooleanVar(value=False)  # Ride sharing desativado por padrão

        algoritmos = [
            ("A* (A-Estrela)", "astar"),
            ("Greedy (Guloso)", "greedy"),
            ("UCS (Uniform Cost)", "ucs"),
            ("BFS (Breadth-First)", "bfs"),
            ("DFS (Depth-First)", "dfs")
        ]

        for nome, valor in algoritmos:
            tk.Radiobutton(
                frame,
                text=nome,
                variable=self.algoritmo_var,
                value=valor,
                bg="#ffffff",
                fg="#4b5563",
                activebackground="#ffffff",
                selectcolor="#f3f4f6",
                font=("Inter", 10),
                command=self.atualizar_algoritmo,
                borderwidth=0,
                highlightthickness=0,
                padx=5
            ).pack(anchor="w", pady=2)

        # Checkboxes para features
        tk.Label(frame, text="",
                bg="#ffffff").pack(pady=5)  # Espaço

        tk.Checkbutton(
            frame,
            text="Reposicionamento Proativo",
            variable=self.reposicionamento_ativo,
            bg="#ffffff",
            fg="#4b5563",
            activebackground="#ffffff",
            selectcolor="#f3f4f6",
            font=("Inter", 10),
            borderwidth=0,
            highlightthickness=0
        ).pack(anchor="w", pady=2)

        tk.Checkbutton(
            frame,
            text="Ride Sharing",
            variable=self.ride_sharing_ativo,
            bg="#ffffff",
            fg="#4b5563",
            activebackground="#ffffff",
            selectcolor="#f3f4f6",
            font=("Inter", 10),
            borderwidth=0,
            highlightthickness=0
        ).pack(anchor="w", pady=2)

        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_frota(self):
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(frame, text="Estado da Frota",
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))

        # Container para os estados
        status_frame = tk.Frame(frame, bg="#f9fafb", relief="flat")
        status_frame.pack(fill="x", pady=5)

        self.label_disponiveis = tk.Label(status_frame, text="Disponíveis: 0",
                                         bg="#f9fafb", fg="#10b981",
                                         font=("Inter", 10))
        self.label_disponiveis.pack(anchor="w", padx=10, pady=3)

        self.label_ocupados = tk.Label(status_frame, text="Ocupados: 0",
                                      bg="#f9fafb", fg="#3b82f6",
                                      font=("Inter", 10))
        self.label_ocupados.pack(anchor="w", padx=10, pady=3)

        self.label_recarregar = tk.Label(status_frame, text="A recarregar: 0",
                                        bg="#f9fafb", fg="#f59e0b",
                                        font=("Inter", 10))
        self.label_recarregar.pack(anchor="w", padx=10, pady=3)

        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_metricas(self):
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(frame, text="Métricas",
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Container grid - 2 colunas, 4 linhas
        grid = tk.Frame(frame, bg="#ffffff")
        grid.pack(fill="x")

        self.metricas_labels = {}

        metricas = [
            ("pedidos", "Pedidos", "#10b981", 0, 0),
            ("taxa", "Taxa Sucesso", "#3b82f6", 0, 1),
            ("km", "Km Total", "#f59e0b", 1, 0),
            ("custo", "Custo", "#8b5cf6", 1, 1),
            ("dead_mileage", "Dead Mileage", "#ef4444", 2, 0),
            ("emissoes", "Emissões CO₂", "#64748b", 2, 1),
            ("tempo_resp", "Tempo Médio", "#06b6d4", 3, 0),
            ("estacoes", "Estações OK", "#22c55e", 3, 1),
            ("ride_sharing", "Ride Sharing", "#ec4899", 4, 0)
        ]

        for key, titulo, cor, row, col in metricas:
            card = tk.Frame(grid, bg="#f9fafb", relief="flat",
                          width=145, height=70)
            card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            card.grid_propagate(False)

            tk.Frame(card, bg=cor, height=3).pack(fill="x")

            tk.Label(card, text=titulo, bg="#f9fafb", fg="#6b7280",
                   font=("Inter", 9)).pack(pady=(8, 2))

            label = tk.Label(card, text="0", bg="#f9fafb", fg="#111827",
                           font=("Inter", 16, "bold"))
            label.pack()

            self.metricas_labels[key] = label

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_pedidos(self):
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="both", expand=False, padx=20, pady=(0, 15))
        
        tk.Label(frame, text="Pedidos Ativos", 
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        list_frame = tk.Frame(frame, bg="#f9fafb", relief="flat")
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, bg="#e5e7eb", troughcolor="#f9fafb")
        scrollbar.pack(side="right", fill="y")
        
        self.list_pedidos = tk.Listbox(
            list_frame,
            height=4,
            yscrollcommand=scrollbar.set,
            font=("Inter", 9),
            bg="#f9fafb",
            fg="#374151",
            selectbackground="#dbeafe",
            selectforeground="#1e40af",
            borderwidth=0,
            highlightthickness=0
        )
        self.list_pedidos.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.list_pedidos.yview)
        
        tk.Frame(self.frame_conteudo, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_eventos(self):
        frame = tk.Frame(self.frame_conteudo, bg="#ffffff")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        tk.Label(frame, text="Eventos", 
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        log_frame = tk.Frame(frame, bg="#f9fafb")
        log_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, bg="#e5e7eb")
        scrollbar.pack(side="right", fill="y")
        
        self.text_log = tk.Text(
            log_frame,
            height=10,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Inter", 9),
            bg="#f9fafb",
            fg="#6b7280",
            insertbackground="#3b82f6",
            borderwidth=0,
            highlightthickness=0,
            padx=8,
            pady=8
        )
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_log.yview)

    def criar_botoes(self):
        frame = self.frame_botoes_fixo

        # Separador antes dos botões
        tk.Frame(frame, bg="#e5e7eb", height=1).pack(fill="x", pady=(0, 15))

        # Controlo de velocidade
        speed_frame = tk.Frame(frame, bg="#ffffff")
        speed_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(speed_frame, text="Velocidade:",
                bg="#ffffff", fg="#6b7280",
                font=("Inter", 9)).pack(side="left")

        for vel in [1, 2, 5]:
            btn = tk.Button(
                speed_frame,
                text=f"{vel}x",
                command=lambda v=vel: self.alterar_velocidade(v),
                bg="#f3f4f6" if vel == 1 else "#ffffff",
                fg="#374151",
                font=("Inter", 9),
                relief="flat",
                bd=1,
                cursor="hand2",
                padx=10,
                pady=4
            )
            btn.pack(side="left", padx=2)
            if vel == 1:
                self.btn_vel_atual = btn

        # Botão Iniciar
        btn_iniciar = tk.Button(
            frame,
            text="▶ Iniciar Simulação",
            command=self.executar_simulacao,
            bg="#10b981",
            fg="#ffffff",
            font=("Inter", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#059669",
            activeforeground="#ffffff",
            padx=20,
            pady=12
        )
        btn_iniciar.pack(fill="x", padx=20, pady=(0, 8))
        
        # Botão Pausar
        btn_pausar = tk.Button(
            frame,
            text="⏸ Pausar",
            command=self.pausar_simulacao,
            bg="#ef4444",
            fg="#ffffff",
            font=("Inter", 10),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#dc2626",
            padx=20,
            pady=10
        )
        btn_pausar.pack(fill="x", padx=20, pady=(0, 15))

    def atualizar_hora_inicial(self):
        """Ativa/desativa spinbox conforme seleção"""
        if self.hora_inicial_var.get() == "escolhida":
            self.hora_escolhida.config(state="normal")
        else:
            self.hora_escolhida.config(state="disabled")

    def atualizar_algoritmo(self):
        algoritmo = self.algoritmo_var.get()
        self.simulador.gestor.definir_algoritmo_procura(algoritmo)
        self.registar_evento(f"Algoritmo alterado: {algoritmo.upper()}")

    def registar_evento(self, msg: str):
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def mostrar_pedido(self, pedido):
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino}"
        items = list(self.list_pedidos.get(0, tk.END))
        if display not in items:
            self.list_pedidos.insert(tk.END, display)
        self.mapa.desenhar_pedido(pedido)

    def remover_pedido_visual(self, pedido):
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino}"
        items = list(self.list_pedidos.get(0, tk.END))
        if display in items:
            self.list_pedidos.delete(items.index(display))
        self.mapa.remover_pedido(pedido)


    def atualizar(self):
        m = self.simulador.gestor.metricas
        metrics = m.calcular_metricas()

        # Tempo
        self.label_tempo.config(
            text=f"Tempo: {self.simulador.tempo_atual}/{self.simulador.duracao_total} min"
        )

        # Hora do dia e trânsito
        if self.simulador.gestor_transito and hasattr(self, 'label_hora'):
            hora = self.simulador.gestor_transito.hora_atual
            self.label_hora.config(text=f"Hora: {hora:02d}:00")

            factor = self.simulador.gestor_transito.calcular_factor_hora(hora)
            if factor >= 1.8:
                self.label_transito.config(text="Transito: RUSH HOUR!", fg="#ef4444")
            elif factor >= 1.3:
                self.label_transito.config(text="Transito: Moderado", fg="#f59e0b")
            elif factor < 1.0:
                self.label_transito.config(text="Transito: Fluido", fg="#10b981")
            else:
                self.label_transito.config(text="Transito: Normal", fg="#6b7280")

        # Estado da Frota
        disponiveis = sum(1 for v in self.simulador.gestor.veiculos.values()
                         if v.estado == EstadoVeiculo.DISPONIVEL)
        ocupados = sum(1 for v in self.simulador.gestor.veiculos.values()
                      if v.estado in (EstadoVeiculo.EM_DESLOCACAO, EstadoVeiculo.A_SERVICO))
        a_recarregar = sum(1 for v in self.simulador.gestor.veiculos.values()
                          if v.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER))

        if hasattr(self, 'label_disponiveis'):
            self.label_disponiveis.config(text=f"Disponíveis: {disponiveis}")
            self.label_ocupados.config(text=f"Ocupados: {ocupados}")
            self.label_recarregar.config(text=f"A recarregar: {a_recarregar}")

        # Métricas
        total = metrics['pedidos_servicos'] + metrics['pedidos_rejeitados']
        self.metricas_labels["pedidos"].config(text=f"{metrics['pedidos_servicos']}/{total}")
        self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
        self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
        self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")

        # Novas métricas
        self.metricas_labels["dead_mileage"].config(
            text=f"{metrics['perc_km_vazio']:.1f}%"
        )
        self.metricas_labels["emissoes"].config(
            text=f"{metrics['emissoes_totais']:.1f}kg"
        )
        self.metricas_labels["tempo_resp"].config(
            text=f"{metrics['tempo_medio_resposta']:.1f}m"
        )

        # Estações disponíveis
        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            total_estacoes = estado['estacoes_recarga']['total'] + estado['postos_abastecimento']['total']
            online_estacoes = estado['estacoes_recarga']['online'] + estado['postos_abastecimento']['online']
            self.metricas_labels["estacoes"].config(text=f"{online_estacoes}/{total_estacoes}")
        else:
            self.metricas_labels["estacoes"].config(text="N/A")

        # Ride Sharing
        if self.simulador.gestor_ride_sharing:
            stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
            self.metricas_labels["ride_sharing"].config(
                text=f"{stats['grupos_criados']} grupos"
            )
        else:
            self.metricas_labels["ride_sharing"].config(text="N/A")

        # Atualiza estações offline no mapa
        estacoes_offline = set()
        if self.simulador.gestor_falhas:
            todas_estacoes = (self.simulador.gestor_falhas.obter_estacoes_recarga() +
                            self.simulador.gestor_falhas.obter_postos_abastecimento())
            for est_id in todas_estacoes:
                no = self.simulador.gestor.grafo.nos[est_id]
                if not no.disponivel:
                    estacoes_offline.add(est_id)
            self.mapa.desenhar_nos(estacoes_offline)

        # Mapa
        pedidos = [p for p in self.simulador.gestor.pedidos_pendentes
                  if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        try:
            self.root.after(self.intervalo_atualizacao, self.atualizar)
        except tk.TclError:
            pass


    def executar_simulacao(self):
        if self.simulador.tempo_atual >= self.simulador.duracao_total:
            self.reiniciar_simulacao()

        # Define hora inicial no gestor de trânsito
        if self.simulador.gestor_transito:
            if self.hora_inicial_var.get() == "aleatoria":
                import random
                hora = random.randint(0, 23)
                self.registar_evento(f"Hora inicial aleatória: {hora}:00")
            else:
                hora = int(self.hora_escolhida.get())
                self.registar_evento(f"Hora inicial escolhida: {hora}:00")

            self.simulador.gestor_transito.hora_inicial = hora
            self.simulador.gestor_transito.hora_atual = hora

        self.simulacao_ativa = True
        self.registar_evento(f"Simulação iniciada com {self.simulador.gestor.algoritmo_procura.upper()}")
        self.executar_passo()

    def executar_passo(self):
        """Executa passos da simulação baseado na velocidade"""
        if not self.simulacao_ativa or self.simulador.tempo_atual > self.simulador.duracao_total:
            if self.simulador.tempo_atual > self.simulador.duracao_total:
                self.finalizar_simulacao()
            return

        # Executa múltiplos passos baseado na velocidade
        passos = self.velocidade
        for _ in range(passos):
            if self.simulador.tempo_atual > self.simulador.duracao_total:
                break
            self._executar_passo_individual()

    def _executar_passo_individual(self):
        """Executa um único passo da simulação (1 minuto)"""

        # Atualiza trânsito
        if self.simulador.gestor_transito:
            self.simulador.gestor_transito.atualizar_transito(self.simulador.tempo_atual)

        # Simula falhas aleatórias em estações (a cada 5 minutos)
        if self.simulador.gestor_falhas and self.simulador.tempo_atual % 5 == 0:
            falhas = self.simulador.gestor_falhas.simular_falha_aleatoria(self.simulador.tempo_atual)
            for est_id in falhas:
                self.registar_evento(f"[t={self.simulador.tempo_atual}] FALHA: {est_id} OFFLINE")

        # Processa simulação (1 minuto)
        self.simulador.processar_pedidos_novos()
        self.simulador.atribuir_pedidos_pendentes()
        self.simulador.mover_veiculos()
        self.simulador.verificar_conclusao_pedidos()
        self.simulador.verificar_recargas()

        # Reposicionamento proativo (a cada 5 minutos) - apenas se ativo
        if self.simulador.tempo_atual % 5 == 0 and self.reposicionamento_ativo.get():
            pedidos_futuros = [p for _, _, _, p in self.simulador.fila_pedidos]
            reposicionamentos = self.simulador.gestor.reposicionar_veiculos(
                self.simulador.tempo_atual, pedidos_futuros
            )
            if reposicionamentos:
                for veiculo_id, origem, destino in reposicionamentos:
                    self.registar_evento(f"[t={self.simulador.tempo_atual}] REPOSICAO: {veiculo_id} {origem}->{destino}")

        pedidos = [p for p in self.simulador.gestor.pedidos_pendentes
                   if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)]

        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)


        self.simulador.tempo_atual += 1

        # Agenda próximo passo (intervalo baseado na velocidade)
        self.root.after(self.intervalo_atualizacao, self.executar_passo)

    def finalizar_simulacao(self):
        """Finaliza simulação e mostra resultados"""
        self.simulacao_ativa = False
        metricas = self.simulador.gestor.metricas.calcular_metricas()

        # Relatório no log
        self.registar_evento("\n" + "="*50)
        self.registar_evento("SIMULAÇÃO TERMINADA")
        self.registar_evento("="*50)
        self.registar_evento(f"Pedidos servidos: {metricas['pedidos_servicos']}")
        self.registar_evento(f"Pedidos rejeitados: {metricas['pedidos_rejeitados']}")
        self.registar_evento(f"Taxa de sucesso: {metricas['taxa_sucesso']}%")
        self.registar_evento(f"Tempo médio resposta: {metricas['tempo_medio_resposta']:.1f} min")
        self.registar_evento(f"Custo total: €{metricas['custo_total']:.2f}")
        self.registar_evento(f"Emissões CO₂: {metricas['emissoes_totais']:.2f} kg")
        self.registar_evento(f"Km totais: {metricas['km_totais']:.2f} km")
        self.registar_evento(f"Dead mileage: {metricas['km_sem_passageiros']:.2f} km ({metricas['perc_km_vazio']:.1f}%)")

        # Estatísticas de falhas
        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            self.registar_evento("\n--- ESTATÍSTICAS DE FALHAS ---")
            self.registar_evento(f"Total de eventos: {estado['total_falhas_historico']}")
            self.registar_evento(f"Estações recarga: {estado['estacoes_recarga']['taxa_disponibilidade']}% disponibilidade")
            self.registar_evento(f"Postos abastecimento: {estado['postos_abastecimento']['taxa_disponibilidade']}% disponibilidade")

        # Popup de resultados
        self.mostrar_relatorio_final(metricas)

    def mostrar_relatorio_final(self, metricas):
        """Mostra popup com relatório final destacado"""
        # Evita múltiplos popups
        if hasattr(self, '_popup_aberto') and self._popup_aberto:
            return
        self._popup_aberto = True

        popup = tk.Toplevel(self.root)
        popup.title("Simulação Concluída")
        popup.geometry("500x600")
        popup.configure(bg="#ffffff")
        popup.transient(self.root)

        # Aguarda janela estar visível antes de grab_set
        popup.update_idletasks()
        try:
            popup.grab_set()
        except:
            pass  # Ignora erro se janela não estiver pronta

        # Header
        header = tk.Frame(popup, bg="#10b981", height=80)
        header.pack(fill="x")
        tk.Label(header, text="✓ Simulação Concluída",
                bg="#10b981", fg="#ffffff",
                font=("Inter", 18, "bold")).pack(pady=25)

        # Conteúdo
        content = tk.Frame(popup, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        resultados = [
            ("Pedidos Atendidos", f"{metricas['pedidos_servicos']}/{metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']}"),
            ("Taxa de Sucesso", f"{metricas['taxa_sucesso']:.1f}%"),
            ("Tempo Médio", f"{metricas['tempo_medio_resposta']:.1f} min"),
            ("Custo Total", f"€{metricas['custo_total']:.2f}"),
            ("Emissões CO₂", f"{metricas['emissoes_totais']:.1f} kg"),
            ("Km Totais", f"{metricas['km_totais']:.1f} km"),
            ("Dead Mileage", f"{metricas['perc_km_vazio']:.1f}%"),
        ]

        for label, valor in resultados:
            row = tk.Frame(content, bg="#ffffff")
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label + ":",
                    bg="#ffffff", fg="#6b7280",
                    font=("Inter", 10)).pack(side="left")
            tk.Label(row, text=valor,
                    bg="#ffffff", fg="#111827",
                    font=("Inter", 10, "bold")).pack(side="right")

        # Botão fechar
        def fechar_popup():
            self._popup_aberto = False
            popup.destroy()

        tk.Button(popup, text="Fechar",
                 command=fechar_popup,
                 bg="#3b82f6", fg="#ffffff",
                 font=("Inter", 11, "bold"),
                 relief="flat", padx=40, pady=12,
                 cursor="hand2").pack(pady=20)

        # Reset flag quando fechar janela
        popup.protocol("WM_DELETE_WINDOW", fechar_popup)

    def reiniciar_simulacao(self):
        self._popup_aberto = False  # Reset flag do popup
        self.simulador.tempo_atual = 0
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []
        
        self.simulador.fila_pedidos = []
        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(self.simulador.fila_pedidos, 
                          (pedido.instante_pedido, -pedido.prioridade, 
                           pedido.id_pedido, pedido))
        
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0
            v.km_sem_passageiros = 0.0
            v.id_pedido_atual = None
            v.tempo_ocupado_ate = 0
        
        self.simulador.gestor.metricas = Metricas()
        self.list_pedidos.delete(0, tk.END)
        self.registar_evento("Simulação reiniciada")

    def pausar_simulacao(self):
        if self.simulacao_ativa:
            self.simulacao_ativa = False
            self.registar_evento("⏸ Simulação PAUSADA")
        else:
            self.simulacao_ativa = True
            self.registar_evento("▶ Simulação RETOMADA")
            self.executar_passo()

    def alterar_velocidade(self, velocidade):
        """Altera velocidade da simulação"""
        self.velocidade = velocidade
        if velocidade == 1:
            self.intervalo_atualizacao = 1000
        elif velocidade == 2:
            self.intervalo_atualizacao = 500
        else:  # 5x
            self.intervalo_atualizacao = 200

        # Atualiza visual dos botões
        for widget in self.btn_vel_atual.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") != "Velocidade:":
                widget.config(bg="#ffffff")

        # Destaca botão selecionado
        for widget in self.btn_vel_atual.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == f"{velocidade}x":
                widget.config(bg="#f3f4f6")
                break

        self.registar_evento(f"⚡ Velocidade alterada para {velocidade}x")

    def iniciar(self):
        """Inicia loop GUI"""
        self.root.mainloop()
