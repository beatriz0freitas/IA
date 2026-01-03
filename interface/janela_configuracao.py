"""
Janelas de configuração pré-simulação para TaxiGreen.
Separadas em duas etapas: Simulação e Pedidos/Features.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class JanelaConfiguracao:
    """
    Janela 1: Configuração da Simulação
    Define parâmetros base: duração, hora inicial, algoritmo, estratégia, trânsito, falhas.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("TaxiGreen - Configuração da Simulação")
        self.root.geometry("550x700")
        self.root.configure(bg="#f9fafb")
        self.root.resizable(False, False)
        
        self.config = {}
        self.continuar = False
        
        self.criar_interface()
        self.centrar_janela()
    
    def centrar_janela(self):
        """Centra janela no ecrã."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def criar_interface(self):
        # Container principal com scroll
        canvas = tk.Canvas(self.root, bg="#f9fafb", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg="#f9fafb")
        
        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header = tk.Frame(frame_scroll, bg="#10b981", height=80)
        header.pack(fill="x")
        tk.Label(
            header, 
            text="⚙️ Configuração da Simulação",
            bg="#10b981", fg="#ffffff",
            font=("Inter", 20, "bold")
        ).pack(pady=25)
        
        # Conteúdo
        content = tk.Frame(frame_scroll, bg="#f9fafb")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # === SECÇÃO 1: DURAÇÃO ===
        self.criar_secao(content, "Duração da Simulação")
        
        self.duracao_var = tk.IntVar(value=60)
        duracao_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        duracao_frame.pack(fill="x", pady=(0, 20))
        
        for duracao in [30, 60, 90, 120]:
            tk.Radiobutton(
                duracao_frame,
                text=f"{duracao} minutos",
                variable=self.duracao_var,
                value=duracao,
                bg="#ffffff", fg="#374151",
                font=("Inter", 10),
                selectcolor="#f3f4f6"
            ).pack(anchor="w", padx=15, pady=3)
        
        # === SECÇÃO 2: HORA INICIAL ===
        self.criar_secao(content, "Hora Inicial do Trânsito")
        
        self.hora_tipo_var = tk.StringVar(value="aleatoria")
        hora_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        hora_frame.pack(fill="x", pady=(0, 20))
        
        tk.Radiobutton(
            hora_frame,
            text="Aleatória (0-23h)",
            variable=self.hora_tipo_var,
            value="aleatoria",
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_hora_spinbox
        ).pack(anchor="w", padx=15, pady=3)
        
        escolher_frame = tk.Frame(hora_frame, bg="#ffffff")
        escolher_frame.pack(anchor="w", padx=15, pady=3)
        
        tk.Radiobutton(
            escolher_frame,
            text="Especificar hora:",
            variable=self.hora_tipo_var,
            value="escolhida",
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_hora_spinbox
        ).pack(side="left")
        
        self.hora_spinbox = tk.Spinbox(
            escolher_frame,
            from_=0, to=23, width=5,
            font=("Inter", 10),
            state="disabled"
        )
        self.hora_spinbox.pack(side="left", padx=5)
        tk.Label(escolher_frame, text="h", bg="#ffffff", fg="#6b7280", 
                font=("Inter", 10)).pack(side="left")
        
        # === SECÇÃO 3: ALGORITMO ===
        self.criar_secao(content, "Algoritmo de Procura")
        
        self.algoritmo_var = tk.StringVar(value="astar")
        algo_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        algo_frame.pack(fill="x", pady=(0, 20))
        
        algoritmos = [
            ("A* (A-Estrela) - Ótimo e eficiente", "astar"),
            ("Greedy - Rápido mas não ótimo", "greedy"),
            ("UCS - Ótimo mas mais lento", "ucs"),
            ("BFS - Não considera custos", "bfs"),
            ("DFS - Exploratório", "dfs")
        ]
        
        for nome, valor in algoritmos:
            tk.Radiobutton(
                algo_frame,
                text=nome,
                variable=self.algoritmo_var,
                value=valor,
                bg="#ffffff", fg="#374151",
                font=("Inter", 10),
                selectcolor="#f3f4f6"
            ).pack(anchor="w", padx=15, pady=3)
        
        # === SECÇÃO 4: ESTRATÉGIA DE SELEÇÃO ===
        self.criar_secao(content, "Estratégia de Seleção de Veículos")
        
        self.estrategia_var = tk.StringVar(value="dead_mileage")
        strat_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        strat_frame.pack(fill="x", pady=(0, 20))
        
        estrategias = [
            ("Minimizar Dead Mileage", "dead_mileage"),
            ("Menor Distância", "menor_distancia"),
            ("Custo Composto", "custo_composto"),
            ("Equilibrada", "equilibrada"),
            ("Priorizar Elétricos", "priorizar_eletricos")
        ]
        
        for nome, valor in estrategias:
            tk.Radiobutton(
                strat_frame,
                text=nome,
                variable=self.estrategia_var,
                value=valor,
                bg="#ffffff", fg="#374151",
                font=("Inter", 10),
                selectcolor="#f3f4f6"
            ).pack(anchor="w", padx=15, pady=3)
        
        # === SECÇÃO 5: VELOCIDADE DA SIMULAÇÃO ===
        self.criar_secao(content, "Velocidade da Simulação")
        
        self.velocidade_var = tk.IntVar(value=1)
        vel_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        vel_frame.pack(fill="x", pady=(0, 20))
        
        velocidades = [
            ("1x - Normal", 1),
            ("2x - Rápida", 2),
            ("5x - Muito Rápida", 5),
            ("10x - Máxima", 10)
        ]
        
        for nome, valor in velocidades:
            tk.Radiobutton(
                vel_frame,
                text=nome,
                variable=self.velocidade_var,
                value=valor,
                bg="#ffffff", fg="#374151",
                font=("Inter", 10),
                selectcolor="#f3f4f6"
            ).pack(anchor="w", padx=15, pady=3)
        
        # Aviso para velocidades altas
        aviso_frame = tk.Frame(vel_frame, bg="#fef3c7", relief="flat")
        aviso_frame.pack(fill="x", padx=15, pady=(8, 0))
        
        tk.Label(
            aviso_frame,
            text="Velocidades > 2x podem reduzir a precisão visual",
            bg="#fef3c7", fg="#92400e",
            font=("Inter", 8, "italic"),
            wraplength=450,
            justify="left"
        ).pack(padx=8, pady=6)

        # === SECÇÃO 6: FEATURES DINÂMICAS ===
        self.criar_secao(content, "Features Dinâmicas")
        
        features_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        features_frame.pack(fill="x", pady=(0, 20))
        
        self.transito_var = tk.BooleanVar(value=True)
        self.falhas_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            features_frame,
            text="Trânsito Dinâmico (varia por hora do dia)",
            variable=self.transito_var,
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_falhas_config
        ).pack(anchor="w", padx=15, pady=5)
        
        tk.Checkbutton(
            features_frame,
            text="Sistema de Falhas em Estações",
            variable=self.falhas_var,
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_falhas_config
        ).pack(anchor="w", padx=15, pady=5)
        
        # Sub-config: Probabilidade de falhas
        self.falhas_config_frame = tk.Frame(features_frame, bg="#f9fafb")
        self.falhas_config_frame.pack(fill="x", padx=30, pady=(5, 0))
        
        tk.Label(
            self.falhas_config_frame,
            text="Probabilidade de falhas:",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 9)
        ).pack(side="left")
        
        self.prob_falha_var = tk.DoubleVar(value=0.08)
        self.prob_falha_spinbox = tk.Spinbox(
            self.falhas_config_frame,
            from_=0.0, to=0.30, increment=0.05,
            width=6, format="%.2f",
            font=("Inter", 9)
        )
        self.prob_falha_spinbox.pack(side="left", padx=5)
        
        # === BOTÕES ===
        btn_frame = tk.Frame(content, bg="#f9fafb")
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(
            btn_frame,
            text="➡️ Continuar para Features",
            command=self.validar_e_continuar,
            bg="#10b981", fg="#ffffff",
            font=("Inter", 12, "bold"),
            relief="flat", cursor="hand2",
            padx=30, pady=12
        ).pack(fill="x")
    
    def criar_secao(self, parent, titulo):
        """Helper para criar cabeçalho de secção."""
        tk.Label(
            parent,
            text=titulo,
            bg="#f9fafb", fg="#111827",
            font=("Inter", 12, "bold")
        ).pack(anchor="w", pady=(10, 8))
    
    def toggle_hora_spinbox(self):
        """Ativa/desativa spinbox de hora."""
        if self.hora_tipo_var.get() == "escolhida":
            self.hora_spinbox.config(state="normal")
        else:
            self.hora_spinbox.config(state="disabled")
    
    def toggle_falhas_config(self):
        """Mostra/oculta configuração de probabilidade de falhas."""
        if self.falhas_var.get():
            self.falhas_config_frame.pack(fill="x", padx=30, pady=(5, 0))
        else:
            self.falhas_config_frame.pack_forget()
    
    def validar_e_continuar(self):
        """Valida configurações e passa para próxima janela."""
        self.config = {
            'duracao': self.duracao_var.get(),
            'hora_tipo': self.hora_tipo_var.get(),
            'hora_escolhida': int(self.hora_spinbox.get()) if self.hora_tipo_var.get() == "escolhida" else None,
            'algoritmo': self.algoritmo_var.get(),
            'estrategia': self.estrategia_var.get(),
            'usar_transito': self.transito_var.get(),
            'usar_falhas': self.falhas_var.get(),
            'prob_falha': float(self.prob_falha_spinbox.get()) if self.falhas_var.get() else 0.0
        }
        
        self.continuar = True
        self.root.destroy()
    
    def obter_config(self) -> Dict[str, Any]:
        """Retorna configurações escolhidas."""
        return self.config


class JanelaFeatures:
    """
    Janela 2: Configuração de Features Avançadas
    Define reposicionamento, ride sharing, e geração de pedidos.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("TaxiGreen - Configuração de Features")
        self.root.geometry("550x650")
        self.root.configure(bg="#f9fafb")
        self.root.resizable(False, False)
        
        self.config = {}
        self.continuar = False
        
        self.criar_interface()
        self.centrar_janela()
    
    def centrar_janela(self):
        """Centra janela no ecrã."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def criar_interface(self):
        # Header
        header = tk.Frame(self.root, bg="#3b82f6", height=80)
        header.pack(fill="x")
        tk.Label(
            header, 
            text="Configuração de Pedidos/Features",
            bg="#3b82f6", fg="#ffffff",
            font=("Inter", 20, "bold")
        ).pack(pady=25)
        
        # Conteúdo
        content = tk.Frame(self.root, bg="#f9fafb")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # === SECÇÃO 1: OTIMIZAÇÕES ===
        self.criar_secao(content, "Otimizações")
        
        opt_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        opt_frame.pack(fill="x", pady=(0, 20))
        
        self.reposicionamento_var = tk.BooleanVar(value=True)
        self.ride_sharing_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(
            opt_frame,
            text="Reposicionamento Proativo",
            variable=self.reposicionamento_var,
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6"
        ).pack(anchor="w", padx=15, pady=5)
        
        tk.Checkbutton(
            opt_frame,
            text="Ride Sharing",
            variable=self.ride_sharing_var,
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_ride_sharing_config
        ).pack(anchor="w", padx=15, pady=5)
        
        # Sub-config: Parâmetros de Ride Sharing
        self.ride_sharing_config_frame = tk.Frame(opt_frame, bg="#f9fafb")
        # Inicialmente oculto
        
        tk.Label(
            self.ride_sharing_config_frame,
            text="Raio de agrupamento (km):",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 9)
        ).grid(row=0, column=0, sticky="w", padx=10, pady=3)
        
        self.raio_var = tk.DoubleVar(value=5.0)
        tk.Spinbox(
            self.ride_sharing_config_frame,
            from_=1.0, to=10.0, increment=0.5,
            textvariable=self.raio_var,
            width=8, font=("Inter", 9)
        ).grid(row=0, column=1, padx=5)
        
        tk.Label(
            self.ride_sharing_config_frame,
            text="Janela temporal (min):",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 9)
        ).grid(row=1, column=0, sticky="w", padx=10, pady=3)
        
        self.janela_var = tk.IntVar(value=10)
        tk.Spinbox(
            self.ride_sharing_config_frame,
            from_=5, to=15, increment=1,
            textvariable=self.janela_var,
            width=8, font=("Inter", 9)
        ).grid(row=1, column=1, padx=5)
        
        # === SECÇÃO 2: GERAÇÃO DE PEDIDOS ===
        self.criar_secao(content, "Geração de Pedidos")
        
        self.pedidos_tipo_var = tk.StringVar(value="demo")
        pedidos_frame = tk.Frame(content, bg="#ffffff", relief="flat")
        pedidos_frame.pack(fill="x", pady=(0, 20))
        
        tk.Radiobutton(
            pedidos_frame,
            text="Usar Pedidos Demo (30 pedidos pré-definidos)",
            variable=self.pedidos_tipo_var,
            value="demo",
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_pedidos_config
        ).pack(anchor="w", padx=15, pady=3)
        
        tk.Radiobutton(
            pedidos_frame,
            text="Gerar Pedidos Aleatórios",
            variable=self.pedidos_tipo_var,
            value="aleatorios",
            bg="#ffffff", fg="#374151",
            font=("Inter", 10),
            selectcolor="#f3f4f6",
            command=self.toggle_pedidos_config
        ).pack(anchor="w", padx=15, pady=3)
        
        # Sub-config: Número de pedidos aleatórios
        self.pedidos_config_frame = tk.Frame(pedidos_frame, bg="#f9fafb")
        # Inicialmente oculto
        
        tk.Label(
            self.pedidos_config_frame,
            text="Número de pedidos:",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 9)
        ).pack(side="left", padx=10)
        
        self.num_pedidos_var = tk.IntVar(value=25)
        tk.Spinbox(
            self.pedidos_config_frame,
            from_=10, to=50, increment=5,
            textvariable=self.num_pedidos_var,
            width=6, font=("Inter", 9)
        ).pack(side="left", padx=5)
        
        # === BOTÕES ===
        btn_frame = tk.Frame(content, bg="#f9fafb")
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(
            btn_frame,
            text="⬅️ Voltar",
            command=self.voltar,
            bg="#64748b", fg="#ffffff",
            font=("Inter", 10, "bold"),
            relief="flat", cursor="hand2",
            padx=20, pady=10
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="Iniciar Simulação",
            command=self.validar_e_iniciar,
            bg="#10b981", fg="#ffffff",
            font=("Inter", 12, "bold"),
            relief="flat", cursor="hand2",
            padx=30, pady=12
        ).pack(side="left", fill="x", expand=True)
    
    def criar_secao(self, parent, titulo):
        """Helper para criar cabeçalho de secção."""
        tk.Label(
            parent,
            text=titulo,
            bg="#f9fafb", fg="#111827",
            font=("Inter", 12, "bold")
        ).pack(anchor="w", pady=(10, 8))
    
    def toggle_ride_sharing_config(self):
        """Mostra/oculta parâmetros de ride sharing."""
        if self.ride_sharing_var.get():
            self.ride_sharing_config_frame.pack(fill="x", padx=30, pady=(5, 10))
        else:
            self.ride_sharing_config_frame.pack_forget()
    
    def toggle_pedidos_config(self):
        """Mostra/oculta configuração de pedidos aleatórios."""
        if self.pedidos_tipo_var.get() == "aleatorios":
            self.pedidos_config_frame.pack(fill="x", padx=30, pady=(5, 0))
        else:
            self.pedidos_config_frame.pack_forget()
    
    def voltar(self):
        """Volta para janela anterior."""
        self.continuar = False
        self.root.destroy()
    
    def validar_e_iniciar(self):
        """Valida configurações e inicia simulação."""
        self.config = {
            'reposicionamento': self.reposicionamento_var.get(),
            'ride_sharing': self.ride_sharing_var.get(),
            'raio_agrupamento': self.raio_var.get() if self.ride_sharing_var.get() else 5.0,
            'janela_temporal': self.janela_var.get() if self.ride_sharing_var.get() else 10,
            'tipo_pedidos': self.pedidos_tipo_var.get(),
            'num_pedidos': self.num_pedidos_var.get() if self.pedidos_tipo_var.get() == "aleatorios" else 0
        }
        
        self.continuar = True
        self.root.destroy()
    
    def obter_config(self) -> Dict[str, Any]:
        """Retorna configurações escolhidas."""
        return self.config


# === FUNÇÃO PRINCIPAL ===
def obter_configuracoes_simulacao() -> Dict[str, Any]:
    """
    Executa as duas janelas de configuração sequencialmente.
    
    Returns:
        Dict com todas as configurações escolhidas ou None se cancelado.
    """
    import random
    
    # Janela 1: Configuração da Simulação
    root1 = tk.Tk()
    janela1 = JanelaConfiguracao(root1)
    root1.mainloop()
    
    if not janela1.continuar:
        return None
    
    config_simulacao = janela1.obter_config()
    
    # Janela 2: Configuração de Pedidos/Features
    root2 = tk.Tk()
    janela2 = JanelaFeatures(root2)
    root2.mainloop()
    
    if not janela2.continuar:
        return None
    
    config_features = janela2.obter_config()
    
    # Combina configurações
    config_completa = {**config_simulacao, **config_features}
    
    # Processa hora inicial
    if config_completa['hora_tipo'] == 'aleatoria':
        config_completa['hora_inicial'] = random.randint(0, 23)
    else:
        config_completa['hora_inicial'] = config_completa['hora_escolhida']
    
    return config_completa