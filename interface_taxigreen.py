# interface_taxigreen.py
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
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1100x720")
        self.root.configure(bg="#ecf4ee")

        self.criar_layout_principal()
        self.root.after(1000, self.atualizar)

    def criar_layout_principal(self):
        # frames
        self.frame_mapa = tk.Frame(self.root, bg="#ecf4ee")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.frame_direita = tk.Frame(self.root, bg="#d6ede0", width=300)
        self.frame_direita.pack(side="right", fill="y", padx=10, pady=10)

        # mapa (InterfaceMapa)
        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo)
        
        # ========== SELEÇÃO DE ALGORITMO ==========
        tk.Label(self.frame_direita, text="Algoritmo de Procura", 
                 bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        self.algoritmo_var = tk.StringVar(value="astar")
        algoritmos = [
            ("A* (A-Estrela)", "astar"),
            ("UCS (Uniform Cost)", "ucs"),
            ("BFS (Breadth-First)", "bfs"),
            ("DFS (Depth-First)", "dfs")
        ]
        
        for nome, valor in algoritmos:
            tk.Radiobutton(
                self.frame_direita,
                text=nome,
                variable=self.algoritmo_var,
                value=valor,
                bg="#d6ede0",
                command=self.atualizar_algoritmo
            ).pack(anchor="w", padx=20)

        tk.Label(self.frame_direita, text="", bg="#d6ede0", height=1).pack()  # espaçador

        # painel de métricas (simples)
        tk.Label(self.frame_direita, text="Métricas", bg="#d6ede0", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.label_metricas = tk.Label(self.frame_direita, text="Sem dados", bg="#d6ede0", justify="left", font=("Arial", 10))
        self.label_metricas.pack(padx=10, pady=5, anchor="w")

        # painel de pedidos ativos
        tk.Label(self.frame_direita, text="Pedidos Ativos", bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(12, 2), anchor="w", padx=10)
        self.list_pedidos = tk.Listbox(self.frame_direita, height=8)
        self.list_pedidos.pack(padx=10, pady=5, fill="x")

        # log / feedback
        tk.Label(self.frame_direita, text="Eventos", bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=10)
        self.text_log = tk.Text(self.frame_direita, height=10, width=36)
        self.text_log.pack(padx=10, pady=5)

        # controlos
        ttk.Button(self.frame_direita, text="Iniciar", command=self.executar_simulacao).pack(padx=10, pady=6, fill="x")
        ttk.Button(self.frame_direita, text="Pausar", command=self.pausar_simulacao).pack(padx=10, pady=2, fill="x")


    def atualizar_algoritmo(self):
        """Chamado quando o utilizador muda o algoritmo selecionado"""
        algoritmo = self.algoritmo_var.get()
        self.simulador.gestor.definir_algoritmo_procura(algoritmo)
        self.registar_evento(f"Algoritmo alterado para: {algoritmo.upper()}")
        
        
    def registar_evento(self, msg: str):
        """Escreve mensagem no log e força refresh leve."""
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        # atualização não bloqueante
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def mostrar_pedido(self, pedido):
        """Adiciona pedido à lista lateral e desenha no mapa."""
        items = list(self.list_pedidos.get(0, tk.END))
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino} [{pedido.pref_ambiental}]"
        if display not in items:
            self.list_pedidos.insert(tk.END, display)
        self.mapa.desenhar_pedido(pedido)

    def remover_pedido_visual(self, pedido):
        items = list(self.list_pedidos.get(0, tk.END))
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino} [{pedido.pref_ambiental}]"
        if display in items:
            idx = items.index(display)
            self.list_pedidos.delete(idx)
        self.mapa.remover_pedido(pedido)


    # Atualiza mapa e métricas (chamado a cada segundo pelo root.after)."""
    def atualizar(self):
        m = self.simulador.gestor.metricas
        metrics = m.calcular_metricas()
        algo_nome = self.simulador.gestor.algoritmo_procura.upper()
        text = (
            f"Algoritmo: {algo_nome}\n"
            f"Pedidos completos: {metrics['pedidos_servicos']}\n"
            f"Pedidos rejeitados: {metrics['pedidos_rejeitados']}\n"
            f"Emissões totais: {metrics['emissoes_totais']:.2f}\n"
            f"Custo total: {metrics['custo_total']:.2f}\n"
            f"Km totais: {metrics['km_totais']:.1f}"
        )
        self.label_metricas.config(text=text)

        pedidos = [p for p in self.simulador.gestor.pedidos_pendentes if p.estado.name == "PENDENTE"]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        try:
            self.root.after(1000, self.atualizar)
        except tk.TclError:
            pass



    def executar_simulacao(self):
        # Se a simulação já terminou, reinicia automaticamente
        if self.simulador.tempo_atual >= self.simulador.duracao_total:
            self.reiniciar_simulacao()
        
        self.registar_evento(f" Iniciar simulação com {self.simulador.gestor.algoritmo_procura.upper()}")
        self.simulador.executar()

    def reiniciar_simulacao(self):
        """Reinicia a simulação do zero (chamado automaticamente se já terminou)"""
        # Reset do tempo e estado
        self.simulador.tempo_atual = 0
        
        # Reset dos pedidos
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []
        
        # Reagendar todos os pedidos
        self.simulador.fila_pedidos = []
        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(self.simulador.fila_pedidos, 
                          (pedido.instante_pedido, -pedido.prioridade, pedido))
        
        # Reset dos veículos (voltar às posições iniciais)
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0
        
        # Reset das métricas
        self.simulador.gestor.metricas = Metricas()
        
        # Limpar interface
        self.list_pedidos.delete(0, tk.END)
        
        self.registar_evento(f"Simulação reiniciada automaticamente")

    def pausar_simulacao(self):
        self.registar_evento("Pausa solicitada (não implementada).")

    def iniciar(self):
        self.root.mainloop()