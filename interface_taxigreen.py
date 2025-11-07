# interface_taxigreen.py
import tkinter as tk
from tkinter import ttk
from interface_mapa import InterfaceMapa

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
        text = (
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
        self.registar_evento("Iniciar simulação")
        self.simulador.executar()

    def pausar_simulacao(self):
        self.registar_evento("Pausa solicitada (não implementada).")

    def iniciar(self):
        self.root.mainloop()