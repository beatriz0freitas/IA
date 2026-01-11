"""
Interface TaxiGreen
"""

import tkinter as tk
from interface.interface_mapa import InterfaceMapa
from interface.interface_componentes import ComponentesUI, GestorPedidosVisuais
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas
import heapq


class InterfaceTaxiGreen:
    WINDOW_W = 1240
    WINDOW_H = 780

    SIDEBAR_W = 450
    SIDEBAR_FOOTER_H = 92  

    PAD_X_OUT = 4
    PAD_Y_OUT = 4
    GAP_X = 3

    def __init__(self, simulador, config: dict):
        self.simulador = simulador
        self.config = config

        self.simulacao_ativa = False
        self.velocidade = config.get("velocidade", 1)
        self.intervalo_atualizacao = self.calcular_intervalo(self.velocidade)

        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}")
        self.root.configure(bg="#f3f4f6")
        self.root.resizable(False, False)

        self.gestor_pedidos_visuais = None

        self.criar_interface()
        self._set_estado_inicial_botoes()
        self.root.after(self.intervalo_atualizacao, self.atualizar)

    def calcular_intervalo(self, velocidade):
        intervalos = {1: 1000, 2: 500, 5: 200, 10: 100}
        return intervalos.get(velocidade, 1000)

    def criar_interface(self):
        # Root: 1 linha, 2 colunas
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        frame_mapa = tk.Frame(self.root, bg="#f3f4f6")
        frame_mapa.grid(
            row=0, column=0, sticky="nsew",
            padx=(self.PAD_X_OUT, self.GAP_X), pady=self.PAD_Y_OUT
        )

        sidebar = tk.Frame(self.root, bg="#ffffff", width=self.SIDEBAR_W)
        sidebar.grid(
            row=0, column=1, sticky="nsew",
            padx=(self.GAP_X, self.PAD_X_OUT), pady=self.PAD_Y_OUT
        )
        sidebar.grid_propagate(False)

        sidebar.grid_rowconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=0, minsize=self.SIDEBAR_FOOTER_H)
        sidebar.grid_columnconfigure(0, weight=1)

        sidebar_content = tk.Frame(sidebar, bg="#ffffff")
        sidebar_content.grid(row=0, column=0, sticky="nsew")

        sidebar_footer = tk.Frame(sidebar, bg="#ffffff", height=self.SIDEBAR_FOOTER_H)
        sidebar_footer.grid(row=1, column=0, sticky="ew")
        sidebar_footer.grid_propagate(False)

        tk.Frame(sidebar_footer, bg="#e5e7eb", height=1).pack(fill="x")

        mapa_w = self.WINDOW_W - self.SIDEBAR_W - (self.PAD_X_OUT * 2) - (self.GAP_X * 2)
        mapa_h = self.WINDOW_H - (self.PAD_Y_OUT * 2)

        self.mapa = InterfaceMapa(
            frame_mapa,
            self.simulador.gestor.grafo,
            width=max(600, mapa_w),
            height=max(520, mapa_h),
        )

        # Sidebar content
        componentes = ComponentesUI(sidebar_content, self.config)

        widgets_header = componentes.criar_header(sidebar_content)
        self.label_tempo = widgets_header["label_tempo"]
        self.label_hora = widgets_header["label_hora"]
        self.label_transito = widgets_header["label_transito"]

        componentes.criar_info_config(sidebar_content, len(self.simulador.fila_pedidos))

        cards_frota = componentes.criar_frota_compacta(sidebar_content)
        self.card_disponiveis = cards_frota["disponiveis"]
        self.card_servico = cards_frota["servico"]
        self.card_recarga = cards_frota["recarga"]
        self.card_indisp = cards_frota["indisp"]

        widgets_pedidos = componentes.criar_pedidos_lista(sidebar_content)
        self.gestor_pedidos_visuais = GestorPedidosVisuais(
            widgets_pedidos["container"],
            widgets_pedidos["canvas"],
            widgets_pedidos["label_contador"],
            componentes,
        )

        self.metricas_labels = componentes.criar_metricas_completas(sidebar_content)
        self.text_log = componentes.criar_log(sidebar_content)

        # Botões (footer da sidebar)
        btn_wrap = tk.Frame(sidebar_footer, bg="#ffffff")
        btn_wrap.pack(fill="both", expand=True, padx=10, pady=8)

        self.btn_iniciar = tk.Button(
            btn_wrap,
            text="Iniciar Simulacao",
            bg="#10b981",
            fg="#ffffff",
            font=("Inter", 10, "bold"),
            relief="flat",
            cursor="hand2",
            pady=7,
            command=self.executar_simulacao,
        )
        self.btn_iniciar.pack(fill="x", pady=(0, 6))

        self.btn_pausar = tk.Button(
            btn_wrap,
            text="Pausar",
            bg="#ef4444",
            fg="#ffffff",
            font=("Inter", 9, "bold"),
            relief="flat",
            cursor="hand2",
            pady=6,
            command=self.pausar_simulacao,
        )
        self.btn_pausar.pack(fill="x")

    def _set_estado_inicial_botoes(self):
        self.btn_iniciar.config(text="Iniciar Simulacao", bg="#10b981", command=self.executar_simulacao)
        self.btn_pausar.config(text="Pausar", bg="#ef4444", command=self.pausar_simulacao)

    def _set_estado_em_execucao_botoes(self):
        self.btn_iniciar.config(text="Acabar Simulacao", bg="#10b981", command=self.acabar_simulacao)

    def registar_evento(self, msg: str):
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def atualizar(self):
        m = self.simulador.gestor.metricas
        metrics = m.calcular_metricas()

        self.label_tempo.config(text=f"{self.simulador.tempo_atual}/{self.config['duracao']} min")

        if self.simulador.gestor_transito:
            hora = self.simulador.gestor_transito.hora_atual
            self.label_hora.config(text=f"Hora: {hora:02d}:00")

            factor = self.simulador.gestor_transito.calcular_factor_hora(hora)
            if factor >= 1.8:
                self.label_transito.config(text="Transito: RUSH!", fg="#ef4444")
            elif factor >= 1.3:
                self.label_transito.config(text="Transito: Moderado", fg="#f59e0b")
            elif factor < 1.0:
                self.label_transito.config(text="Transito: Fluido", fg="#10b981")
            else:
                self.label_transito.config(text="Transito: Normal", fg="#6b7280")

        veiculos = self.simulador.gestor.veiculos.values()
        total = len(veiculos)

        disponiveis = sum(1 for v in veiculos if v.estado == EstadoVeiculo.DISPONIVEL)
        servico = sum(1 for v in veiculos if v.estado in (EstadoVeiculo.EM_DESLOCACAO, EstadoVeiculo.A_SERVICO))
        recarga = sum(1 for v in veiculos if v.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER))
        indisp = sum(1 for v in veiculos if v.estado == EstadoVeiculo.INDISPONIVEL)

        self.card_disponiveis.config(text=f"{disponiveis}/{total}")
        self.card_servico.config(text=str(servico))
        self.card_recarga.config(text=str(recarga))
        self.card_indisp.config(text=str(indisp))

        pedidos_ativos = [
            p for p in self.simulador.gestor.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)
        ]
        self.gestor_pedidos_visuais.atualizar(pedidos_ativos)

        total_pedidos = metrics["pedidos_servicos"] + metrics["pedidos_rejeitados"]
        self.metricas_labels["pedidos"].config(text=f"{metrics['pedidos_servicos']}/{total_pedidos}")
        self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
        self.metricas_labels["tempo_resp"].config(text=f"{metrics['tempo_medio_resposta']:.1f}m")
        self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
        self.metricas_labels["dead_mileage"].config(text=f"{metrics['perc_km_vazio']:.1f}%")
        self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")
        self.metricas_labels["emissoes"].config(text=f"{metrics['emissoes_totais']:.1f}kg")

        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            total_est = estado["estacoes_recarga"]["total"] + estado["postos_abastecimento"]["total"]
            online_est = estado["estacoes_recarga"]["online"] + estado["postos_abastecimento"]["online"]
            self.metricas_labels["estacoes"].config(text=f"{online_est}/{total_est}")

        if "ride_sharing" in self.metricas_labels and self.simulador.gestor_ride_sharing:
            stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
            self.metricas_labels["ride_sharing"].config(text=str(stats["grupos_criados"]))

        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos_ativos)

        try:
            self.root.after(self.intervalo_atualizacao, self.atualizar)
        except tk.TclError:
            pass

    def executar_simulacao(self):
        if self.simulador.tempo_atual >= self.config["duracao"]:
            self.reiniciar_simulacao()

        self.simulacao_ativa = True
        self._set_estado_em_execucao_botoes()
        self.btn_pausar.config(text="Pausar", bg="#ef4444")

        self.registar_evento(f"Simulacao iniciada ({self.velocidade}x)")
        self.executar_passo()

    def acabar_simulacao(self):
        if not self.simulacao_ativa:
            return
        self.simulacao_ativa = False
        self.registar_evento("SIMULACAO TERMINADA PELO UTILIZADOR")
        self._set_estado_inicial_botoes()

    def executar_passo(self):
        if not self.simulacao_ativa or self.simulador.tempo_atual > self.config["duracao"]:
            if self.simulador.tempo_atual > self.config["duracao"]:
                self.finalizar_simulacao()
            return

        for _ in range(self.velocidade):
            if self.simulador.tempo_atual > self.config["duracao"]:
                break
            self.executar_passo_individual()

    def executar_passo_individual(self):
        if self.simulador.gestor_transito:
            self.simulador.gestor_transito.atualizar_transito(self.simulador.tempo_atual)

        if self.simulador.gestor_falhas and self.simulador.tempo_atual % 5 == 0:
            falhas = self.simulador.gestor_falhas.simular_falha_aleatoria(self.simulador.tempo_atual)
            for est_id in falhas:
                self.registar_evento(f"[t={self.simulador.tempo_atual}] {est_id} OFFLINE")

        self.simulador.processar_pedidos_novos()
        self.simulador.atribuir_pedidos_pendentes()
        self.simulador.mover_veiculos()
        self.simulador.verificar_conclusao_pedidos()
        self.simulador.verificar_recargas()

        if self.simulador.tempo_atual % 5 == 0 and self.config.get("reposicionamento", False):
            pedidos_futuros = [p for _, _, _, p in self.simulador.fila_pedidos]
            self.simulador.gestor.reposicionar_veiculos(self.simulador.tempo_atual, pedidos_futuros)

        self.simulador.tempo_atual += 1
        self.root.after(self.intervalo_atualizacao, self.executar_passo)

    def pausar_simulacao(self):
        if not self.simulacao_ativa:
            return

        if self.btn_pausar.cget("text") == "Pausar":
            self.simulacao_ativa = False
            self.btn_pausar.config(text="Retomar", bg="#10b981")
            self.registar_evento("PAUSADA")
        else:
            self.simulacao_ativa = True
            self.btn_pausar.config(text="Pausar", bg="#ef4444")
            self.registar_evento("RETOMADA")
            self.executar_passo()

    def finalizar_simulacao(self):
        self.simulacao_ativa = False
        self._set_estado_inicial_botoes()

        metricas = self.simulador.gestor.metricas.calcular_metricas()
        self.registar_evento("\n" + "=" * 40)
        self.registar_evento(" SIMULACAO CONCLUIDA")
        self.registar_evento("=" * 40)
        self.registar_evento(f"Servidos: {metricas['pedidos_servicos']}")
        self.registar_evento(f"Rejeitados: {metricas['pedidos_rejeitados']}")
        self.registar_evento(f"Taxa: {metricas['taxa_sucesso']}%")

        self.mostrar_popup_resultados(metricas)

    def mostrar_popup_resultados(self, metricas):
        popup = tk.Toplevel(self.root)
        popup.title("Simulacao Concluida")
        popup.geometry("480x550")
        popup.configure(bg="#ffffff")
        popup.transient(self.root)
        popup.resizable(False, False)

        tk.Frame(popup, bg="#10b981", height=60).pack(fill="x")
        tk.Label(
            popup, text="Simulacao Concluida",
            bg="#10b981", fg="#ffffff",
            font=("Inter", 15, "bold")
        ).place(x=240, y=20, anchor="center")

        content = tk.Frame(popup, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        resultados = [
            ("Pedidos Atendidos", f"{metricas['pedidos_servicos']}/{metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']}"),
            ("Taxa de Sucesso", f"{metricas['taxa_sucesso']:.1f}%"),
            ("Tempo Medio", f"{metricas['tempo_medio_resposta']:.1f} min"),
            ("Custo Total", f"€{metricas['custo_total']:.2f}"),
            ("Emissoes CO2", f"{metricas['emissoes_totais']:.1f} kg"),
            ("Km Totais", f"{metricas['km_totais']:.1f} km"),
            ("Dead Mileage", f"{metricas['perc_km_vazio']:.1f}%"),
        ]

        for label, valor in resultados:
            row = tk.Frame(content, bg="#ffffff")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label + ":", bg="#ffffff", fg="#6b7280", font=("Inter", 9)).pack(side="left")
            tk.Label(row, text=valor, bg="#ffffff", fg="#111827", font=("Inter", 9, "bold")).pack(side="right")

        tk.Button(
            popup, text="Fechar",
            command=popup.destroy,
            bg="#3b82f6", fg="#ffffff",
            font=("Inter", 9, "bold"),
            relief="flat", padx=30, pady=8,
            cursor="hand2"
        ).pack(pady=15)

    def reiniciar_simulacao(self):
        self.simulador.tempo_atual = 0
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []

        self.simulador.fila_pedidos = []
        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(
                self.simulador.fila_pedidos,
                (pedido.instante_pedido, -pedido.prioridade, pedido.id_pedido, pedido)
            )

        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0

        self.simulador.gestor.metricas = Metricas()
        self.gestor_pedidos_visuais.limpar()
        self.registar_evento("Simulacao reiniciada")

    def iniciar(self):
        self.root.mainloop()