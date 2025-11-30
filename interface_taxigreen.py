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
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1300x800")
        self.root.configure(bg="#f9fafb")
        
        self.criar_layout_principal()
        self.root.after(1000, self.atualizar)

    def criar_layout_principal(self):
        
        # ===== MAPA =====
        self.frame_mapa = tk.Frame(self.root, bg="#f9fafb")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo, width=900, height=700)
        
        # ===== SIDEBAR =====
        self.frame_direita = tk.Frame(self.root, bg="#ffffff", width=350)
        self.frame_direita.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.frame_direita.pack_propagate(False)
        
        self.criar_header()
        self.criar_secao_algoritmo()
        self.criar_secao_metricas()
        self.criar_secao_pedidos()
        self.criar_secao_eventos()
        self.criar_botoes()

    def criar_header(self):
        header = tk.Frame(self.frame_direita, bg="#ffffff")
        header.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header, text="TaxiGreen", 
                bg="#ffffff", fg="#111827",
                font=("Inter", 18, "bold")).pack(anchor="w")
        
        self.label_tempo = tk.Label(header, text="Tempo: 0/12 min", 
                                   bg="#ffffff", fg="#6b7280",
                                   font=("Inter", 11))
        self.label_tempo.pack(anchor="w", pady=(2, 0))
        
        tk.Frame(self.frame_direita, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 15))

    def criar_secao_algoritmo(self):
        frame = tk.Frame(self.frame_direita, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(frame, text="Algoritmo de Procura", 
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        self.algoritmo_var = tk.StringVar(value="astar")
        
        algoritmos = [
            ("A* (A-Estrela)", "astar"),
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
        
        tk.Frame(self.frame_direita, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_metricas(self):
        frame = tk.Frame(self.frame_direita, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(frame, text="Métricas", 
                bg="#ffffff", fg="#374151",
                font=("Inter", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Container grid
        grid = tk.Frame(frame, bg="#ffffff")
        grid.pack(fill="x")
        
        self.metricas_labels = {}
        
        metricas = [
            ("pedidos", "Pedidos", "#10b981", 0, 0),
            ("taxa", "Taxa Sucesso", "#3b82f6", 0, 1),
            ("km", "Km Total", "#f59e0b", 1, 0),
            ("custo", "Custo", "#8b5cf6", 1, 1)
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
        
        tk.Frame(self.frame_direita, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_pedidos(self):
        frame = tk.Frame(self.frame_direita, bg="#ffffff")
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
        
        tk.Frame(self.frame_direita, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=15)

    def criar_secao_eventos(self):
        frame = tk.Frame(self.frame_direita, bg="#ffffff")
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
        frame = tk.Frame(self.frame_direita, bg="#ffffff")
        frame.pack(fill="x", padx=20, pady=15)
        
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
        btn_iniciar.pack(fill="x", pady=(0, 8))
        
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
        btn_pausar.pack(fill="x")

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
        
        # Métricas
        total = metrics['pedidos_servicos'] + metrics['pedidos_rejeitados']
        self.metricas_labels["pedidos"].config(text=f"{metrics['pedidos_servicos']}/{total}")
        self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
        self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
        self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")
        
        # Mapa
        pedidos = [p for p in self.simulador.gestor.pedidos_pendentes 
                  if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        try:
            self.root.after(1000, self.atualizar)
        except tk.TclError:
            pass


    def executar_simulacao(self):
        if self.simulador.tempo_atual >= self.simulador.duracao_total:
            self.reiniciar_simulacao()
        
        self.registar_evento(f"Simulação iniciada com {self.simulador.gestor.algoritmo_procura.upper()}")
        self.simulador.executar()

    def reiniciar_simulacao(self):
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
            v.pedido_atual = None
            v.tempo_ocupado_ate = 0
        
        self.simulador.gestor.metricas = Metricas()
        self.list_pedidos.delete(0, tk.END)
        self.registar_evento("Simulação reiniciada")

    def pausar_simulacao(self):
        self.registar_evento("Pausa não implementada")

    def iniciar(self):
        """Inicia loop GUI"""
        self.root.mainloop()
