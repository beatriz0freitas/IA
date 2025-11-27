# interface_taxigreen.py
import tkinter as tk
from tkinter import ttk
import heapq
from interface_mapa import InterfaceMapa
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas

"""Interface Tkinter para visualização da simulação TaxiGreen"""
class InterfaceTaxiGreen:

    def __init__(self, simulador):
        self.simulador = simulador
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1100x720")
        self.root.configure(bg="#ecf4ee")

        self.criar_layout_principal()
        self.root.after(1000, self.atualizar)

    """Cria layout em dois painéis: mapa (esquerda) e controles (direita)"""
    def criar_layout_principal(self):

        # ===== PAINEL ESQUERDO: MAPA =====
        self.frame_mapa = tk.Frame(self.root, bg="#ecf4ee")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.frame_direita = tk.Frame(self.root, bg="#d6ede0", width=300)
        self.frame_direita.pack(side="right", fill="y", padx=10, pady=10)

        # mapa (InterfaceMapa)
        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo)
        
            # ========== SELEÇÃO DE ALGORITMO ==========
        frame_algoritmo = tk.Frame(self.frame_direita, bg="#d6ede0")
        frame_algoritmo.pack(pady=(10, 5), fill="x")

        tk.Label(frame_algoritmo, text="Algoritmo de Procura", 
                bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(0, 8))

        self.algoritmo_var = tk.StringVar(value="astar")
        algoritmos = [
            ("A* (A-Estrela)", "astar"),
            ("UCS (Uniform Cost)", "ucs"),
            ("BFS (Breadth-First)", "bfs"),
            ("DFS (Depth-First)", "dfs")
        ]

        for nome, valor in algoritmos:
            tk.Radiobutton(
                frame_algoritmo,
                text=nome,
                variable=self.algoritmo_var,
                value=valor,
                bg="#d6ede0",
                activebackground="#d6ede0",
                selectcolor="#90EE90",  # ✨ Verde quando selecionado
                font=("Arial", 10),
                command=self.atualizar_algoritmo
            ).pack(anchor="w", padx=20, pady=2)

        tk.Frame(self.frame_direita, bg="#a8d5ba", height=2).pack(fill="x", pady=10)
        
        # painel de métricas
        tk.Label(self.frame_direita, text="Métricas", bg="#d6ede0", font=("Arial", 13, "bold")).pack(pady=(5, 5))

        frame_metricas = tk.Frame(self.frame_direita, bg="white", relief="solid", borderwidth=1)
        frame_metricas.pack(padx=10, pady=5, fill="x")

        self.label_metricas = tk.Label(frame_metricas, text="Sem dados", 
                                    bg="white", justify="left", font=("Arial", 9))
        self.label_metricas.pack(padx=8, pady=8, anchor="w")

        # painel de pedidos ativos
        tk.Label(self.frame_direita, text="Pedidos Ativos", bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        # Frame com scrollbar
        frame_pedidos = tk.Frame(self.frame_direita)
        frame_pedidos.pack(padx=10, pady=5, fill="both", expand=False)

        scrollbar_pedidos = tk.Scrollbar(frame_pedidos)
        scrollbar_pedidos.pack(side="right", fill="y")

        self.list_pedidos = tk.Listbox(frame_pedidos, height=6, yscrollcommand=scrollbar_pedidos.set, font=("Arial", 9))
        self.list_pedidos.pack(side="left", fill="both", expand=True)
        scrollbar_pedidos.config(command=self.list_pedidos.yview)
        
        # log / feedback
        tk.Label(self.frame_direita, text="Eventos", bg="#d6ede0", font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w", padx=10)

        # Frame com scrollbar
        frame_log = tk.Frame(self.frame_direita)
        frame_log.pack(padx=10, pady=5, fill="both", expand=True)

        scrollbar_log = tk.Scrollbar(frame_log)
        scrollbar_log.pack(side="right", fill="y")

        self.text_log = tk.Text(frame_log, height=10, width=36, 
                                wrap="word", yscrollcommand=scrollbar_log.set, font=("Arial", 8))
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar_log.config(command=self.text_log.yview)

        # controlos
        frame_botoes = tk.Frame(self.frame_direita, bg="#d6ede0")
        frame_botoes.pack(padx=10, pady=10, fill="x")

        btn_iniciar = tk.Button(frame_botoes, text="▶ Iniciar Simulação", 
                                command=self.executar_simulacao,
                                bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                                relief="raised", bd=2, cursor="hand2")
        btn_iniciar.pack(fill="x", pady=3)

        btn_pausar = tk.Button(frame_botoes, text="⏸ Pausar", 
                            command=self.pausar_simulacao,
                            bg="#FF9800", fg="white", font=("Arial", 10),
                            relief="raised", bd=2, cursor="hand2")
        btn_pausar.pack(fill="x", pady=3)

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

    # Adiciona pedido à lista lateral e desenha no mapa.
    def mostrar_pedido(self, pedido):
        items = list(self.list_pedidos.get(0, tk.END))
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino} [{pedido.pref_ambiental}]"
        if display not in items:
            self.list_pedidos.insert(tk.END, display)
        self.mapa.desenhar_pedido(pedido)

    """Remove pedido da lista e mapa"""
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
            f"Tempo: {self.simulador.tempo_atual}/{self.simulador.duracao_total} min\n"

            f"\n PEDIDOS:\n"
            f"Pedidos completos: {metrics['pedidos_servicos']}\n"
            f"Pedidos rejeitados: {metrics['pedidos_rejeitados']}\n"
            f"Taxa sucesso: {metrics['taxa_sucesso']}%\n"
            f"Tempo médio: {metrics['tempo_medio_resposta']} min\n"

            f"\n OPERAÇÃO:\n"
            f"Km totais: {metrics['km_totais']:.1f}\n"
            f"Km vazios: {metrics['km_sem_passageiros']:.1f}\n"
            f"% vazio: {metrics['perc_km_vazio']}%\n"

            f"Emissões totais: {metrics['emissoes_totais']:.2f}\n"
            f"Custo total: {metrics['custo_total']:.2f}\n"
        )
        self.label_metricas.config(text=text)

        pedidos = [p for p in self.simulador.gestor.pedidos_pendentes 
                   if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        try:
            self.root.after(1000, self.atualizar)
        except tk.TclError:
            pass


    # Se a simulação já terminou, reinicia automaticamente
    def executar_simulacao(self):
        if self.simulador.tempo_atual >= self.simulador.duracao_total:
            self.reiniciar_simulacao()
        
        self.registar_evento(f" Iniciar simulação com {self.simulador.gestor.algoritmo_procura.upper()}")
        self.simulador.executar()


    """Reinicia a simulação do zero (chamado automaticamente se já terminou)"""
    def reiniciar_simulacao(self):
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
                          (pedido.instante_pedido, -pedido.prioridade, pedido.id_pedido, pedido))
        
        # Reset dos veículos (voltar às posições iniciais)
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0
            v.km_sem_passageiros = 0.0
            v.id_pedido_atual = None
            v.tempo_ocupado_ate = 0

        # Reset das métricas
        self.simulador.gestor.metricas = Metricas()
        
        # Limpar interface
        self.list_pedidos.delete(0, tk.END)
        
        self.registar_evento(f"Simulação reiniciada automaticamente")

    # TODO: implementar pausa
    def pausar_simulacao(self):
        self.registar_evento("Pausa solicitada (não implementada).")

    """Inicia loop da GUI"""
    def iniciar(self):
        self.root.mainloop()