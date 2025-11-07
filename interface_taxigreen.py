import tkinter as tk
from tkinter import ttk
from interface_mapa import InterfaceMapa

class InterfaceTaxiGreen:
    def __init__(self, simulador):
        self.simulador = simulador
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1200x750")
        self.root.configure(bg="#ecf4ee")

        self.criar_layout_principal()
        self.atualizar()


    def criar_layout_principal(self):
        # Layout principal — 3 zonas
        self.frame_topo = tk.Frame(self.root, bg="#ecf4ee", height=60)
        self.frame_topo.pack(side="top", fill="x", padx=20, pady=(10, 0))

        self.frame_centro = tk.Frame(self.root, bg="#ecf4ee")
        self.frame_centro.pack(fill="both", expand=True, padx=20, pady=10)

        self.frame_base = tk.Frame(self.root, bg="#ecf4ee", height=70)
        self.frame_base.pack(side="bottom", fill="x", padx=20, pady=(0, 10))

        # Topo — título
        titulo = tk.Label(
            self.frame_topo,
            text="Simulação TaxiGreen",
            font=("Helvetica", 20, "bold"),
            bg="#ecf4ee",
            fg="#2a5c3e"
        )
        titulo.pack(anchor="center")

        # Centro — mapa e métricas
        self.frame_mapa = tk.Frame(self.frame_centro, bg="#e8f6ec", bd=2, relief="groove")
        self.frame_mapa.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.frame_metricas = tk.Frame(self.frame_centro, bg="#dcefe4", width=280, bd=2, relief="ridge")
        self.frame_metricas.pack(side="right", fill="y")


        self.mapa = InterfaceMapa(self.frame_mapa, self.simulador.gestor.grafo)
        self.mapa.pack(fill="both", expand=True, padx=10, pady=10)

        self.criar_painel_metricas()
        self.criar_painel_controlo()



    def criar_painel_metricas(self):
        tk.Label(
            self.frame_metricas,
            text="Estatísticas",
            font=("Arial", 15, "bold"),
            bg="#dcefe4",
            fg="#2a5c3e"
        ).pack(pady=10)

        separador = ttk.Separator(self.frame_metricas, orient="horizontal")
        separador.pack(fill="x", padx=10, pady=5)

        self.text_metricas = tk.Label(
            self.frame_metricas,
            text="Aguardando dados...",
            justify="left",
            font=("Arial", 11),
            bg="#dcefe4",
            fg="#333"
        )
        self.text_metricas.pack(padx=15, pady=10, anchor="nw")



    def criar_painel_controlo(self):
        ttk.Style().configure("TButton", font=("Arial", 11), padding=6)

        ttk.Button(self.frame_base, text="Iniciar", command=self.executar_simulacao).pack(side="left", padx=10)
        ttk.Button(self.frame_base, text="Pausar", command=self.pausar_simulacao).pack(side="left", padx=10)
        ttk.Button(self.frame_base, text="Reset", command=self.resetar_simulacao).pack(side="left", padx=10)
        ttk.Button(self.frame_base, text="Sair", command=self.root.destroy).pack(side="right", padx=10)

    def executar_simulacao(self):
        print("Simulação iniciada...")
        self.simulador.executar()

    def pausar_simulacao(self):
        print("Simulação pausada (não implementada).")

    def resetar_simulacao(self):
        print("Reset ao estado da simulação (não implementada).")

    def iniciar(self):
        self.root.mainloop()


    def atualizar(self):
        m = self.simulador.gestor.metricas

        self.text_metricas.config(text=(
            f"Pedidos concluídos: {m.pedidos_servicos}\n"
            f"Pedidos rejeitados: {m.pedidos_rejeitados}\n"
            f"Emissões totais: {m.emissoes_totais:.2f}\n"
            f"Custo total: {m.custo_total:.2f}\n"
            f"Km totais: {m.km_totais:.2f}\n"
            f"Taxa de sucesso: {m.calcular_metricas()['taxa_sucesso']:.2f}"
        ))

        self.mapa.atualizar_veiculos(self.simulador.gestor.veiculos)
        self.root.after(1000, self.atualizar)




