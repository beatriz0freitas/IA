"""
Interface gráfica refatorizada - Remove imports cíclicos
"""

import tkinter as tk
from tkinter import ttk
import heapq
import threading

from interface_mapa import InterfaceMapa
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas

"""Interface Tkinter para visualização da simulação TaxiGreen"""
class InterfaceTaxiGreen:

    def __init__(self, simulador):
        self.simulador = simulador
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator - Gestão de Frota Inteligente")
        self.root.geometry("1100x720")
        self.root.configure(bg="#ecf4ee")

        self.simulacao_thread = None
        self.atualizacoes_fila = []  # fila de mensagens para atualizar

        self.criar_layout_principal()
        self.root.after(500, self.atualizar_periodicamente)

    """Cria layout em dois painéis: mapa (esquerda) e controles (direita)"""
    def criar_layout_principal(self):

        # ===== PAINEL ESQUERDO: MAPA =====
        self.frame_mapa = tk.Frame(self.root, bg="#ecf4ee")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo)

        # ===== PAINEL DIREITO: CONTROLES =====
        self.frame_direita = tk.Frame(self.root, bg="#d6ede0", width=300)
        self.frame_direita.pack(side="right", fill="y", padx=10, pady=10)
        self.frame_direita.pack_propagate(False)


        # --- Seleção de Algoritmo ---
        frame_algo = tk.Frame(self.frame_direita, bg="#d6ede0")
        frame_algo.pack(pady=(10, 5), fill="x")

        tk.Label(
            frame_algo, text="Algoritmo de Procura",
            bg="#d6ede0", font=("Arial", 12, "bold")
        ).pack(pady=(0, 8))

        self.algoritmo_var = tk.StringVar(value="astar")
        algoritmos = [
            ("A* (A-Estrela)", "astar"),
            ("UCS (Uniform Cost)", "ucs"),
            ("BFS (Breadth-First)", "bfs"),
            ("DFS (Depth-First)", "dfs")
        ]

        for nome, valor in algoritmos:
            tk.Radiobutton(
                frame_algo, text=nome, variable=self.algoritmo_var, value=valor,
                bg="#d6ede0", activebackground="#d6ede0",
                selectcolor="#90EE90", font=("Arial", 10),
                command=self._atualizar_algoritmo
            ).pack(anchor="w", padx=20, pady=2)

        tk.Frame(self.frame_direita, bg="#a8d5ba", height=2).pack(fill="x", pady=10)

        # --- Métricas ---
        tk.Label(
            self.frame_direita, text="Métricas",
            bg="#d6ede0", font=("Arial", 13, "bold")
        ).pack(pady=(5, 5))

        frame_metricas = tk.Frame(
            self.frame_direita, bg="white", relief="solid", borderwidth=1
        )
        frame_metricas.pack(padx=10, pady=5, fill="x")

        self.label_metricas = tk.Label(
            frame_metricas, text="Aguardando simulação...",
            bg="white", justify="left", font=("Arial", 9)
        )
        self.label_metricas.pack(padx=8, pady=8, anchor="w")

        # --- Pedidos Ativos ---
        tk.Label(
            self.frame_direita, text="Pedidos Ativos",
            bg="#d6ede0", font=("Arial", 12, "bold")
        ).pack(pady=(10, 5), anchor="w", padx=10)

        frame_pedidos = tk.Frame(self.frame_direita)
        frame_pedidos.pack(padx=10, pady=5, fill="both", expand=False)

        scrollbar_pedidos = tk.Scrollbar(frame_pedidos)
        scrollbar_pedidos.pack(side="right", fill="y")

        self.list_pedidos = tk.Listbox(
            frame_pedidos, height=6, yscrollcommand=scrollbar_pedidos.set,
            font=("Arial", 9)
        )
        self.list_pedidos.pack(side="left", fill="both", expand=True)
        scrollbar_pedidos.config(command=self.list_pedidos.yview)

        # --- Log de Eventos ---
        tk.Label(
            self.frame_direita, text="Eventos",
            bg="#d6ede0", font=("Arial", 12, "bold")
        ).pack(pady=(10, 5), anchor="w", padx=10)

        frame_log = tk.Frame(self.frame_direita)
        frame_log.pack(padx=10, pady=5, fill="both", expand=True)

        scrollbar_log = tk.Scrollbar(frame_log)
        scrollbar_log.pack(side="right", fill="y")

        self.text_log = tk.Text(
            frame_log, height=10, width=36, wrap="word",
            yscrollcommand=scrollbar_log.set, font=("Arial", 8)
        )
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar_log.config(command=self.text_log.yview)

        # --- Botões de Controle ---
        frame_botoes = tk.Frame(self.frame_direita, bg="#d6ede0")
        frame_botoes.pack(padx=10, pady=10, fill="x")

        self.btn_iniciar = tk.Button(
            frame_botoes, text="▶ Iniciar Simulação",
            command=self._executar_simulacao,
            bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
            relief="raised", bd=2, cursor="hand2"
        )
        self.btn_iniciar.pack(fill="x", pady=3)

        self.btn_pausar = tk.Button(
            frame_botoes, text="Pausar",
            command=self._pausar_simulacao,
            bg="#FF9800", fg="white", font=("Arial", 10),
            relief="raised", bd=2, cursor="hand2", state="disabled"
        )
        self.btn_pausar.pack(fill="x", pady=3)

        self.btn_reset = tk.Button(
            frame_botoes, text="Reiniciar",
            command=self._reiniciar_simulacao,
            bg="#2196F3", fg="white", font=("Arial", 10),
            relief="raised", bd=2, cursor="hand2"
        )
        self.btn_reset.pack(fill="x", pady=3)

    """Muda o algoritmo de procura"""
    def atualizar_algoritmo(self):
        algo = self.algoritmo_var.get()
        self.simulador.gestor.definir_algoritmo_procura(algo)
        self.registar_evento(f"Algoritmo alterado para: {algo.upper()}")
    
    """Escreve evento no log"""
    def registar_evento(self, msg: str):
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    # Adiciona pedido à lista lateral e desenha no mapa.
    def mostrar_pedido(self, pedido):
        items = list(self.list_pedidos.get(0, tk.END))
        display = (
            f"{pedido.id_pedido}: {pedido.posicao_inicial} → "
            f"{pedido.posicao_destino} [{pedido.pref_ambiental}]"
        )
        if display not in items:
            self.list_pedidos.insert(tk.END, display)
        self.mapa.desenhar_pedido(pedido)

    """Remove pedido da lista e mapa"""
    def remover_pedido_visual(self, pedido):
        items = list(self.list_pedidos.get(0, tk.END))
        display = (
            f"{pedido.id_pedido}: {pedido.posicao_inicial} → "
            f"{pedido.posicao_destino} [{pedido.pref_ambiental}]"
        )
        if display in items:
            idx = items.index(display)
            self.list_pedidos.delete(idx)
        self.mapa.remover_pedido(pedido)

    """Chamado pela simulação para atualizar visualização"""
    def atualizar_renderizacao(self):
        try:
            m = self.simulador.gestor.metricas
            metrics = m.calcular_metricas()
            algo = self.simulador.gestor.algoritmo_procura.upper()

            text = (
                f"Tempo: {self.simulador.tempo_atual}/{self.simulador.duracao_total} min\n"
                f"Algoritmo: {algo}\n"
                f"Pedidos completos: {metrics['pedidos_servicos']}\n"
                f"Pedidos rejeitados: {metrics['pedidos_rejeitados']}\n"
                f"Emissões: {metrics['emissoes_totais']:.2f} kg CO2\n"
                f"Custo: €{metrics['custo_total']:.2f}\n"
                f"Km: {metrics['km_totais']:.1f}"
            )
            self.label_metricas.config(text=text)

            pedidos = [
                p for p in self.simulador.gestor.pedidos_pendentes
                if p.estado.name == "PENDENTE"
            ]
            self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)
        except tk.TclError:
            pass

    """Atualiza interface a cada 500ms"""
    def atualizar_periodicamente(self):
        try:
            if self.root.winfo_exists():
                self.atualizar_renderizacao()
                self.root.after(500, self.atualizar_periodicamente)
        except tk.TclError:
            pass

    """Inicia simulação em thread separada"""
    def executar_simulacao(self):
        if self.simulacao_thread and self.simulacao_thread.is_alive():
            self.registar_evento("Simulação já está em curso")
            return

        if self.simulador.tempo_atual >= self.simulador.duracao_total:
            self.reiniciar_simulacao()

        self.btn_iniciar.config(state="disabled")
        self.btn_pausar.config(state="normal")

        self.simulacao_thread = threading.Thread(
            target=self.simulador.executar, daemon=False
        )
        self.simulacao_thread.start()

    """Pausa a simulação"""
    def pausar_simulacao(self):
        self.simulador.pausar()
        self.btn_iniciar.config(state="normal")
        self.btn_pausar.config(state="disabled")
        self.registar_evento("Simulação pausada")
    
    """Reinicia simulação do zero"""
    def reiniciar_simulacao(self):
        self.simulador.tempo_atual = 0
        self.simulador.em_execucao = False

        # Reset pedidos
        self.simulador.fila_pedidos = []
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []

        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(
                self.simulador.fila_pedidos,
                (pedido.instante_pedido, -pedido.prioridade, pedido)
            )

        # Reset veículos
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0

        # Reset métricas
        self.simulador.gestor.metricas = Metricas()

        # Reset interface
        self.list_pedidos.delete(0, tk.END)
        self.text_log.delete(1.0, tk.END)
        self.btn_iniciar.config(state="normal")
        self.btn_pausar.config(state="disabled")

        self.registar_evento("Simulação reiniciada")

    """Inicia loop da GUI"""
    def iniciar(self):
        self.root.mainloop()