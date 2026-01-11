"""
Componentes UI - TaxiGreen
Interface limpa, compacta e completamente visível.
"""

import tkinter as tk
from modelo.veiculos import EstadoVeiculo
from modelo.pedidos import EstadoPedido


class ComponentesUI:
    """Componentes UI otimizados para visualização completa."""

    def __init__(self, parent, config: dict):
        self.parent = parent
        self.config = config

    def criar_header(self, container) -> dict:
        """Header compacto com informações essenciais."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=12, pady=8)

        row1 = tk.Frame(frame, bg="#ffffff")
        row1.pack(fill="x")

        tk.Label(
            row1, text="TaxiGreen Simulator",
            bg="#ffffff", fg="#111827",
            font=("Inter", 13, "bold")
        ).pack(side="left")

        label_tempo = tk.Label(
            row1, text="0/60 min",
            bg="#ffffff", fg="#6b7280",
            font=("Inter", 10)
        )
        label_tempo.pack(side="right")

        row2 = tk.Frame(frame, bg="#ffffff")
        row2.pack(fill="x", pady=(2, 0))

        label_hora = tk.Label(
            row2, text="Hora: 00:00",
            bg="#ffffff", fg="#6b7280",
            font=("Inter", 8)
        )
        label_hora.pack(side="left")

        label_transito = tk.Label(
            row2, text="Transito: Normal",
            bg="#ffffff", fg="#10b981",
            font=("Inter", 8, "bold")
        )
        label_transito.pack(side="right")

        self._separador(container, 8)

        return {
            'label_tempo': label_tempo,
            'label_hora': label_hora,
            'label_transito': label_transito
        }

    def criar_info_config(self, container, num_pedidos: int) -> None:
        """Painel com configuração detalhada da simulação."""
        frame = tk.Frame(container, bg="#f9fafb")
        frame.pack(fill="x", padx=12, pady=(0, 8))

        header = tk.Frame(frame, bg="#f9fafb")
        header.pack(fill="x", padx=8, pady=(6, 4))

        tk.Label(
            header, text="CONFIGURACAO",
            bg="#f9fafb", fg="#111827",
            font=("Inter", 9, "bold")
        ).pack(side="left")

        grid = tk.Frame(frame, bg="#f9fafb")
        grid.pack(fill="x", padx=8, pady=(0, 6))

        config_items = [
            ("Algoritmo:", self.config['algoritmo'].upper(), 0, 0),
            ("Duracao:", f"{self.config['duracao']} min", 0, 1),
            ("Estrategia:", self._formatar_estrategia(self.config['estrategia']), 1, 0),
            ("Velocidade:", f"{self.config.get('velocidade', 1)}x", 1, 1),
            ("Pedidos:", f"{num_pedidos}", 2, 0),
            ("Tipo:", self.config['tipo_pedidos'].title(), 2, 1),
        ]

        for label, valor, row, col in config_items:
            cell = tk.Frame(grid, bg="#f9fafb")
            cell.grid(row=row, column=col, sticky="w", padx=4, pady=2)

            tk.Label(
                cell, text=label,
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 7)
            ).pack(side="left")

            tk.Label(
                cell, text=valor,
                bg="#f9fafb", fg="#111827",
                font=("Inter", 7, "bold")
            ).pack(side="left", padx=(3, 0))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        features = []
        if self.config['usar_transito']:
            features.append("Transito")
        if self.config['usar_falhas']:
            features.append("Falhas")
        if self.config.get('reposicionamento'):
            features.append("Repos.")
        if self.config.get('ride_sharing'):
            features.append("R-Share")

        if features:
            feat_frame = tk.Frame(frame, bg="#f9fafb")
            feat_frame.pack(fill="x", padx=8, pady=(2, 6))

            tk.Label(
                feat_frame, text="Features:",
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 7)
            ).pack(side="left", padx=(0, 4))

            for feat in features:
                badge = tk.Label(
                    feat_frame, text=feat,
                    bg="#dbeafe", fg="#1e40af",
                    font=("Inter", 6, "bold"),
                    padx=4, pady=1
                )
                badge.pack(side="left", padx=1)

        self._separador(container, 8)

    def _formatar_estrategia(self, estrategia: str) -> str:
        nomes = {
            'menor_distancia': 'Menor Dist',
            'custo_composto': 'Custo Comp',
            'dead_mileage': 'Dead Mile',
            'equilibrada': 'Equilibrada',
            'priorizar_eletricos': 'Prio Eletr'
        }
        return nomes.get(estrategia, estrategia)

    def criar_frota_compacta(self, container) -> dict:
        """Estado da frota em formato compacto."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(
            frame, text="ESTADO DA FROTA",
            bg="#ffffff", fg="#111827",
            font=("Inter", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        grid = tk.Frame(frame, bg="#ffffff")
        grid.pack(fill="x")

        cards = {}
        items = [
            ("disponiveis", "Disponiveis", "0/4", "#10b981", 0, 0),
            ("servico", "Em Servico", "0", "#3b82f6", 0, 1),
            ("recarga", "Recarregando", "0", "#f59e0b", 1, 0),
            ("indisp", "Indisponiveis", "0", "#64748b", 1, 1),
        ]

        for key, titulo, valor, cor, row, col in items:
            card = tk.Frame(grid, bg="#f9fafb", relief="flat", height=45)
            card.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            card.grid_propagate(False)

            tk.Frame(card, bg=cor, height=2).pack(fill="x")

            tk.Label(
                card, text=titulo,
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 7)
            ).pack(pady=(3, 0))

            label = tk.Label(
                card, text=valor,
                bg="#f9fafb", fg=cor,
                font=("Inter", 11, "bold")
            )
            label.pack()

            cards[key] = label

        grid.columnconfigure(0, weight=1, uniform="col")
        grid.columnconfigure(1, weight=1, uniform="col")

        self._separador(container, 8)

        return cards

    # PEDIDOS ATIVOS - 3 COLUNAS
    def criar_pedidos_lista(self, container) -> dict:
        """Lista de pedidos ativos com scroll (3 colunas antes de precisar scroll)."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=12, pady=(0, 8))

        header = tk.Frame(frame, bg="#ffffff")
        header.pack(fill="x", pady=(0, 4))

        tk.Label(
            header, text="PEDIDOS ATIVOS",
            bg="#ffffff", fg="#111827",
            font=("Inter", 9, "bold")
        ).pack(side="left")

        label_contador = tk.Label(
            header, text="0",
            bg="#dbeafe", fg="#1e40af",
            font=("Inter", 7, "bold"),
            padx=5, pady=1
        )
        label_contador.pack(side="right")

        # Altura um pouco maior para ficar proporcional (imagem atual)
        canvas = tk.Canvas(frame, bg="#f9fafb", highlightthickness=0, height=90)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)

        pedidos_frame = tk.Frame(canvas, bg="#f9fafb")
        pedidos_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 3 colunas iguais
        for c in range(3):
            pedidos_frame.columnconfigure(c, weight=1, uniform="pedido_col")

        canvas.create_window((0, 0), window=pedidos_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._separador(container, 8)

        return {
            'label_contador': label_contador,
            'container': pedidos_frame,
            'canvas': canvas
        }

    def criar_card_pedido(self, container, pedido) -> tk.Frame:
        """Cria card compacto (NÃO faz pack: o gestor posiciona via grid)."""
        card = tk.Frame(container, bg="#ffffff", relief="solid", bd=1)

        cores_prioridade = {3: "#ef4444", 2: "#f59e0b", 1: "#3b82f6", 0: "#9ca3af"}
        cor = cores_prioridade.get(pedido.prioridade, "#9ca3af")
        tk.Frame(card, bg=cor, height=2).pack(fill="x")

        content = tk.Frame(card, bg="#ffffff")
        content.pack(fill="x", padx=5, pady=3)

        row1 = tk.Frame(content, bg="#ffffff")
        row1.pack(fill="x")

        tk.Label(
            row1, text=pedido.id_pedido,
            bg="#ffffff", fg="#111827",
            font=("Inter", 8, "bold")
        ).pack(side="left")

        estado_info = self._get_estado_info(pedido.estado)
        tk.Label(
            row1, text=estado_info['texto'],
            bg=estado_info['bg'], fg=estado_info['fg'],
            font=("Inter", 6, "bold"),
            padx=4, pady=1
        ).pack(side="right")

        rota_text = f"{pedido.posicao_inicial[:12]} -> {pedido.posicao_destino[:12]}"
        tk.Label(
            content, text=rota_text,
            bg="#ffffff", fg="#6b7280",
            font=("Inter", 7)
        ).pack(anchor="w")

        detalhes = tk.Frame(content, bg="#ffffff")
        detalhes.pack(fill="x", pady=(2, 0))

        tk.Label(
            detalhes, text=f"Pass: {pedido.passageiros}",
            bg="#ffffff", fg="#3b82f6",
            font=("Inter", 6, "bold")
        ).pack(side="left", padx=(0, 5))

        if pedido.prioridade >= 2:
            tk.Label(
                detalhes, text=f"Prio.{pedido.prioridade}",
                bg="#ffffff", fg=cor,
                font=("Inter", 6, "bold")
            ).pack(side="left", padx=(0, 5))

        if pedido.veiculo_atribuido:
            tk.Label(
                detalhes, text=pedido.veiculo_atribuido,
                bg="#ffffff", fg="#10b981",
                font=("Inter", 6, "bold")
            ).pack(side="left")

        return card

    def _get_estado_info(self, estado):
        info = {
            EstadoPedido.PENDENTE: {'texto': 'PEND', 'bg': '#fef3c7', 'fg': '#92400e'},
            EstadoPedido.ATRIBUIDO: {'texto': 'ATRIB', 'bg': '#dbeafe', 'fg': '#1e40af'},
            EstadoPedido.EM_EXECUCAO: {'texto': 'EXEC', 'bg': '#d1fae5', 'fg': '#065f46'},
            EstadoPedido.CONCLUIDO: {'texto': 'OK', 'bg': '#e0e7ff', 'fg': '#4338ca'}
        }
        return info.get(estado, {'texto': '?', 'bg': '#f3f4f6', 'fg': '#6b7280'})

    def criar_metricas_completas(self, container) -> dict:
        """Métricas em grid 2 colunas, bem organizadas."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(
            frame, text="METRICAS",
            bg="#ffffff", fg="#111827",
            font=("Inter", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        grid = tk.Frame(frame, bg="#ffffff")
        grid.pack(fill="x")

        metricas_labels = {}

        metricas = [
            ("pedidos", "Pedidos", "0/0", "#10b981", 0, 0),
            ("taxa", "Taxa", "0%", "#3b82f6", 0, 1),
            ("tempo_resp", "T.Resp", "0m", "#06b6d4", 1, 0),
            ("km", "Km", "0", "#f59e0b", 1, 1),
            ("dead_mileage", "Dead", "0%", "#ef4444", 2, 0),
            ("custo", "Custo", "€0", "#8b5cf6", 2, 1),
            ("emissoes", "CO2", "0kg", "#64748b", 3, 0),
            ("estacoes", "Estac", "0/0", "#22c55e", 3, 1),
        ]

        if self.config.get('ride_sharing', False):
            metricas.append(("ride_sharing", "R-Shr", "0", "#ec4899", 4, 0))

        for key, titulo, valor, cor, row, col in metricas:
            card = tk.Frame(grid, bg="#f9fafb", relief="flat", height=42)
            card.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            card.grid_propagate(False)

            tk.Frame(card, bg=cor, height=2).pack(fill="x")

            tk.Label(
                card, text=titulo,
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 7)
            ).pack(pady=(2, 0))

            label = tk.Label(
                card, text=valor,
                bg="#f9fafb", fg=cor,
                font=("Inter", 10, "bold")
            )
            label.pack()

            metricas_labels[key] = label

        grid.columnconfigure(0, weight=1, uniform="col")
        grid.columnconfigure(1, weight=1, uniform="col")

        self._separador(container, 8)

        return metricas_labels

    def criar_log(self, container) -> tk.Text:
        """Log de eventos compacto (ligeiramente mais baixo para dar espaço aos pedidos)."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        tk.Label(
            frame, text="LOG DE EVENTOS",
            bg="#ffffff", fg="#111827",
            font=("Inter", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        log_frame = tk.Frame(frame, bg="#f9fafb")
        log_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        # Menos linhas, porque agora "Pedidos" ocupa mais altura
        text_log = tk.Text(
            log_frame,
            height=4,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 7),
            bg="#f9fafb",
            fg="#374151",
            borderwidth=0,
            highlightthickness=0,
            padx=4,
            pady=4
        )
        text_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_log.yview)

        return text_log

    def criar_botoes(self, container) -> dict:
        """Botões de controlo."""
        self._separador(container, 8)

        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=12, pady=(0, 8))

        btn_iniciar = tk.Button(
            frame, text="Iniciar Simulacao",
            bg="#10b981", fg="#ffffff",
            font=("Inter", 9, "bold"),
            relief="flat", cursor="hand2",
            pady=8
        )
        btn_iniciar.pack(fill="x", pady=(0, 3))

        btn_pausar = tk.Button(
            frame, text="Pausar",
            bg="#ef4444", fg="#ffffff",
            font=("Inter", 8, "bold"),
            relief="flat", cursor="hand2",
            pady=6
        )
        btn_pausar.pack(fill="x")

        return {'btn_iniciar': btn_iniciar, 'btn_pausar': btn_pausar}

    def _separador(self, parent, pady=8):
        tk.Frame(parent, bg="#e5e7eb", height=1).pack(fill="x", padx=12, pady=pady)


class GestorPedidosVisuais:
    """Gere visualização de pedidos (agora em 3 colunas com grid)."""

    def __init__(self, container, canvas, contador, componentes):
        self.container = container
        self.canvas = canvas
        self.contador = contador
        self.componentes = componentes
        self.cards = {}  # id -> widget

        self.num_colunas = 3
        for c in range(self.num_colunas):
            self.container.columnconfigure(c, weight=1, uniform="pedido_col")

    def atualizar(self, pedidos):
        ids_atuais = {p.id_pedido for p in pedidos}
        ids_existentes = set(self.cards.keys())

        for pid in ids_existentes - ids_atuais:
            self.cards[pid].destroy()
            del self.cards[pid]

        for pedido in pedidos:
            if pedido.id_pedido not in self.cards:
                card = self.componentes.criar_card_pedido(self.container, pedido)
                self.cards[pedido.id_pedido] = card

        # reposiciona em 3 colunas (lado a lado)
        for i, pedido in enumerate(pedidos):
            card = self.cards.get(pedido.id_pedido)
            if not card:
                continue
            row = i // self.num_colunas
            col = i % self.num_colunas
            card.grid(row=row, column=col, sticky="ew", padx=3, pady=2)

        self.contador.config(text=str(len(pedidos)))
        self.container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def limpar(self):
        for card in self.cards.values():
            card.destroy()
        self.cards.clear()
        self.contador.config(text="0")
        self.container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))