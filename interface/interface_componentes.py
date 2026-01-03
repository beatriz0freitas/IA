"""
Componentes UI da Interface TaxiGreen
Responsabilidade: Criação e gestão dos elementos visuais (widgets, frames, layouts)
"""

import tkinter as tk
from modelo.veiculos import EstadoVeiculo


class ComponentesUI:
    """
    Classe responsável por criar todos os componentes visuais da interface.
    Separada da lógica de simulação.
    """
    
    def __init__(self, parent, config: dict):
        self.parent = parent
        self.config = config
        self.widgets = {}  # Referências para widgets que precisam ser atualizados
        
    def criar_header(self, container) -> dict:
        """Cria header com título e informações de tempo/hora."""
        header = tk.Frame(container, bg="#ffffff")
        header.pack(fill="x", padx=20, pady=15)

        tk.Label(
            header, text="TaxiGreen",
            bg="#ffffff", fg="#111827",
            font=("Inter", 18, "bold")
        ).pack(anchor="w")

        label_tempo = tk.Label(
            header, 
            text=f"Tempo: 0/{self.config['duracao']} min",
            bg="#ffffff", fg="#6b7280",
            font=("Inter", 11)
        )
        label_tempo.pack(anchor="w", pady=(2, 0))

        # Trânsito e Hora
        info_frame = tk.Frame(header, bg="#ffffff")
        info_frame.pack(anchor="w", pady=(4, 0))

        label_hora = tk.Label(
            info_frame, 
            text=f"Hora: {self.config['hora_inicial']:02d}:00",
            bg="#ffffff", fg="#6b7280",
            font=("Helvetica", 10)
        )
        label_hora.pack(side="left", padx=(0, 10))

        label_transito = tk.Label(
            info_frame, text="Trânsito: Normal",
            bg="#ffffff", fg="#10b981",
            font=("Helvetica", 10, "bold")
        )
        label_transito.pack(side="left")

        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 15))
        
        return {
            'label_tempo': label_tempo,
            'label_hora': label_hora,
            'label_transito': label_transito
        }
    
    def criar_painel_estado(self, container, num_pedidos: int) -> dict:
        """Cria painel com estado/configuração da simulação."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        # Cabeçalho
        header_frame = tk.Frame(frame, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_frame, 
            text="⚙️ Estado da Simulação",
            bg="#ffffff", fg="#374151",
            font=("Inter", 11, "bold")
        ).pack(side="left")

        # Botão collapse/expand
        painel_expandido = tk.BooleanVar(value=True)
        btn_toggle = tk.Label(
            header_frame,
            text="▼",
            bg="#ffffff", fg="#9ca3af",
            font=("Inter", 10),
            cursor="hand2"
        )
        btn_toggle.pack(side="right")

        # Container do conteúdo
        painel_container = tk.Frame(frame, bg="#f9fafb", relief="flat")
        painel_container.pack(fill="x", pady=(5, 0))

        # Grid 2 colunas
        info_items = [
            ("Algoritmo:", self.config['algoritmo'].upper()),
            ("Estratégia:", self.formatar_estrategia(self.config['estrategia'])),
            ("Pedidos:", f"{self.config['tipo_pedidos'].title()} ({num_pedidos})"),
            ("Duração:", f"{self.config['duracao']} min"),
            ("Velocidade:", f"{self.config.get('velocidade', 1)}x"),
        ]

        for i, (label, valor) in enumerate(info_items):
            row = i // 2
            col = i % 2
            
            item_frame = tk.Frame(painel_container, bg="#f9fafb")
            item_frame.grid(row=row, column=col, sticky="w", padx=8, pady=4)
            
            tk.Label(
                item_frame, text=label,
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 8)
            ).pack(side="left")
            
            tk.Label(
                item_frame, text=valor,
                bg="#f9fafb", fg="#111827",
                font=("Inter", 8, "bold")
            ).pack(side="left", padx=(3, 0))

        # Features ativas (badges)
        features_frame = tk.Frame(painel_container, bg="#f9fafb")
        features_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 5))

        tk.Label(
            features_frame, text="Features:",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 8)
        ).pack(side="left", padx=(0, 5))

        self.criar_badges_features(features_frame)

        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 15))
        
        # Bind para toggle
        def toggle():
            if painel_expandido.get():
                painel_container.pack_forget()
                btn_toggle.config(text="▶")
                painel_expandido.set(False)
            else:
                painel_container.pack(fill="x", pady=(5, 0))
                btn_toggle.config(text="▼")
                painel_expandido.set(True)
        
        btn_toggle.bind("<Button-1>", lambda e: toggle())
        
        return {'painel_expandido': painel_expandido}
    
    def criar_badges_features(self, parent):
        """Cria badges coloridos para features ativas."""
        features_ativas = []
        
        if self.config['usar_transito']:
            features_ativas.append(("Trânsito", "#3b82f6"))
        
        if self.config['usar_falhas']:
            features_ativas.append(("Falhas", "#ef4444"))
        
        if self.config['reposicionamento']:
            features_ativas.append(("Repos.", "#10b981"))
        
        if self.config['ride_sharing']:
            features_ativas.append(("R-Share", "#8b5cf6"))

        if not features_ativas:
            tk.Label(
                parent, text="Nenhuma",
                bg="#f9fafb", fg="#9ca3af",
                font=("Inter", 8, "italic")
            ).pack(side="left")
        else:
            for texto, cor in features_ativas:
                badge = tk.Frame(parent, bg=cor, relief="flat")
                badge.pack(side="left", padx=2)
                
                tk.Label(
                    badge, text=f"{texto}",
                    bg=cor, fg="#ffffff",
                    font=("Inter", 7, "bold"),
                    padx=6, pady=2
                ).pack()
    
    def criar_secao_frota(self, container) -> dict:
        """Cria secção de estado da frota."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            frame, text="Estado da Frota",
            bg="#ffffff", fg="#374151",
            font=("Inter", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        status_frame = tk.Frame(frame, bg="#f9fafb", relief="flat")
        status_frame.pack(fill="x", pady=5)

        label_disponiveis = tk.Label(
            status_frame, text="Disponíveis: 0",
            bg="#f9fafb", fg="#10b981",
            font=("Inter", 10)
        )
        label_disponiveis.pack(anchor="w", padx=10, pady=3)

        label_ocupados = tk.Label(
            status_frame, text="Ocupados: 0",
            bg="#f9fafb", fg="#3b82f6",
            font=("Inter", 10)
        )
        label_ocupados.pack(anchor="w", padx=10, pady=3)

        label_recarregar = tk.Label(
            status_frame, text="A recarregar: 0",
            bg="#f9fafb", fg="#f59e0b",
            font=("Inter", 10)
        )
        label_recarregar.pack(anchor="w", padx=10, pady=3)

        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)
        
        return {
            'label_disponiveis': label_disponiveis,
            'label_ocupados': label_ocupados,
            'label_recarregar': label_recarregar
        }
    
    def criar_secao_metricas(self, container) -> dict:
        """Cria secção de métricas com cards."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            frame, text="Métricas",
            bg="#ffffff", fg="#374151",
            font=("Inter", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(frame, bg="#ffffff")
        grid.pack(fill="x")

        metricas_labels = {}

        metricas = [
            ("pedidos", "Pedidos", "#10b981", 0, 0),
            ("taxa", "Taxa Sucesso", "#3b82f6", 0, 1),
            ("km", "Km Total", "#f59e0b", 1, 0),
            ("custo", "Custo", "#8b5cf6", 1, 1),
            ("dead_mileage", "Dead Mileage", "#ef4444", 2, 0),
            ("emissoes", "Emissões CO₂", "#64748b", 2, 1),
            ("tempo_resp", "Tempo Médio", "#06b6d4", 3, 0),
            ("estacoes", "Estações OK", "#22c55e", 3, 1),
        ]
        
        if self.config.get('ride_sharing', False):
            metricas.append(("ride_sharing", "Ride Sharing", "#ec4899", 4, 0))

        for key, titulo, cor, row, col in metricas:
            card = tk.Frame(grid, bg="#f9fafb", relief="flat", width=145, height=70)
            card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            card.grid_propagate(False)

            tk.Frame(card, bg=cor, height=3).pack(fill="x")

            tk.Label(
                card, text=titulo, 
                bg="#f9fafb", fg="#6b7280",
                font=("Inter", 9)
            ).pack(pady=(8, 2))

            label = tk.Label(
                card, text="0", 
                bg="#f9fafb", fg="#111827",
                font=("Inter", 16, "bold")
            )
            label.pack()

            metricas_labels[key] = label

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)
        
        return metricas_labels
    
    def criar_secao_pedidos(self, container) -> tk.Listbox:
        """Cria secção de pedidos ativos."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="both", expand=False, padx=20, pady=(0, 15))
        
        tk.Label(
            frame, text="Pedidos Ativos", 
            bg="#ffffff", fg="#374151",
            font=("Inter", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))
        
        list_frame = tk.Frame(frame, bg="#f9fafb", relief="flat")
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, bg="#e5e7eb", troughcolor="#f9fafb")
        scrollbar.pack(side="right", fill="y")
        
        list_pedidos = tk.Listbox(
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
        list_pedidos.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=list_pedidos.yview)
        
        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)
        
        return list_pedidos
    
    def criar_secao_eventos(self, container) -> tk.Text:
        """Cria secção de log de eventos."""
        frame = tk.Frame(container, bg="#ffffff")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        tk.Label(
            frame, text="Eventos", 
            bg="#ffffff", fg="#374151",
            font=("Inter", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))
        
        log_frame = tk.Frame(frame, bg="#f9fafb")
        log_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, bg="#e5e7eb")
        scrollbar.pack(side="right", fill="y")
        
        text_log = tk.Text(
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
        text_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_log.yview)
        
        return text_log
    
    def criar_botoes(self, container, velocidade: int) -> dict:
        """Cria botões de controlo."""
        tk.Frame(container, bg="#e5e7eb", height=1).pack(fill="x", pady=(0, 15))

        # Info de velocidade
        info_frame = tk.Frame(container, bg="#f3f4f6")
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(
            info_frame,
            text=f"⚡ Velocidade: {velocidade}x (definida na configuração)",
            bg="#f3f4f6", fg="#6b7280",
            font=("Inter", 9)
        ).pack(pady=8)

        # Botão Iniciar
        btn_iniciar = tk.Button(
            container,
            text="▶ Iniciar Simulação",
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
            container,
            text="⏸ Pausar",
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
        
        return {
            'btn_iniciar': btn_iniciar,
            'btn_pausar': btn_pausar
        }
    
    def formatar_estrategia(self, estrategia: str) -> str:
        """Formata nome da estratégia para exibição."""
        nomes = {
            'menor_distancia': 'Menor Dist.',
            'custo_composto': 'Custo Multi',
            'dead_mileage': 'Min. Dead Mile',
            'equilibrada': 'Equilibrada',
            'priorizar_eletricos': 'Prio. Elétricos'
        }
        return nomes.get(estrategia, estrategia.title())