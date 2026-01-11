"""
Interface TaxiGreen
"""

import tkinter as tk
import heapq

from interface.interface_mapa import InterfaceMapa
from interface.interface_componentes import ComponentesUI, GestorPedidosVisuais
from interface.interface_controller import InterfaceController

from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas


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
        self.simulacao_bloqueada = False
        self.velocidade = config.get("velocidade", 1)
        self.intervalo_atualizacao = self.calcular_intervalo(self.velocidade)

        self._a_fechar = False

        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}")
        self.root.configure(bg="#f3f4f6")
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.sair_aplicacao)

        self.ui_scheduler = InterfaceController(self.root)
        self.step_scheduler = InterfaceController(self.root)

        self.gestor_pedidos_visuais = None

        self.criar_interface()
        self._set_estado_inicial_botoes()

        self.ui_scheduler.schedule(self.intervalo_atualizacao, self.atualizar)

    def calcular_intervalo(self, velocidade):
        intervalos = {1: 1000, 2: 500, 5: 200, 10: 100}
        return intervalos.get(velocidade, 1000)

    # -------------------- lifecycle --------------------

    def sair_aplicacao(self):
        """Fecha a aplicação de forma segura."""
        if self._a_fechar:
            return
        self._a_fechar = True

        # Para todas as operações
        self.simulacao_ativa = False
        self.ui_scheduler.cancel()
        self.step_scheduler.cancel()

        try:
            self.root.destroy()
        except tk.TclError:
            pass

    # -------------------- UI build --------------------

    def criar_interface(self):
        """Cria toda a interface gráfica."""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Frame do mapa
        frame_mapa = tk.Frame(self.root, bg="#f3f4f6")
        frame_mapa.grid(
            row=0, column=0, sticky="nsew",
            padx=(self.PAD_X_OUT, self.GAP_X), pady=self.PAD_Y_OUT
        )

        # Sidebar
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

        # Dimensões do mapa
        mapa_w = self.WINDOW_W - self.SIDEBAR_W - (self.PAD_X_OUT * 2) - (self.GAP_X * 2)
        mapa_h = self.WINDOW_H - (self.PAD_Y_OUT * 2)

        self.mapa = InterfaceMapa(
            frame_mapa,
            self.simulador.gestor.grafo,
            width=max(600, mapa_w),
            height=max(520, mapa_h),
        )

        componentes = ComponentesUI(sidebar_content, self.config)

        # Header com tempo e trânsito
        widgets_header = componentes.criar_header(sidebar_content)
        self.label_tempo = widgets_header["label_tempo"]
        self.label_hora = widgets_header["label_hora"]
        self.label_transito = widgets_header["label_transito"]

        # Info configuração
        componentes.criar_info_config(sidebar_content, len(self.simulador.fila_pedidos))

        # Cards da frota
        cards_frota = componentes.criar_frota_compacta(sidebar_content)
        self.card_disponiveis = cards_frota["disponiveis"]
        self.card_servico = cards_frota["servico"]
        self.card_recarga = cards_frota["recarga"]
        self.card_indisp = cards_frota["indisp"]

        # Lista de pedidos
        widgets_pedidos = componentes.criar_pedidos_lista(sidebar_content)
        self.gestor_pedidos_visuais = GestorPedidosVisuais(
            widgets_pedidos["container"],
            widgets_pedidos["canvas"],
            widgets_pedidos["label_contador"],
            componentes,
        )

        # Métricas
        self.metricas_labels = componentes.criar_metricas_completas(sidebar_content)
        
        # Log
        self.text_log = componentes.criar_log(sidebar_content)

        # Botões de controle
        btn_wrap = tk.Frame(sidebar_footer, bg="#ffffff")
        btn_wrap.pack(fill="both", expand=True, padx=10, pady=8)

        self.btn_iniciar = tk.Button(
            btn_wrap,
            text="Iniciar Simulação",
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

    # -------------------- button states --------------------

    def _set_estado_inicial_botoes(self):
        """Estado inicial: pronto para iniciar."""
        self.btn_iniciar.config(
            text="Iniciar Simulação",
            bg="#10b981",
            command=self.executar_simulacao,
            state="normal"
        )
        self.btn_pausar.config(
            text="Pausar",
            bg="#9ca3af",
            state="disabled"
        )

    def _set_estado_em_execucao_botoes(self):
        """Estado em execução: pode acabar ou pausar."""
        self.btn_iniciar.config(
            text="Acabar Simulação",
            bg="#ef4444",
            command=self.acabar_simulacao,
            state="normal"
        )
        self.btn_pausar.config(
            text="Pausar",
            bg="#f59e0b",
            command=self.pausar_simulacao,
            state="normal"
        )

    def _set_estado_pausado_botoes(self):
        """Estado pausado: pode retomar ou acabar."""
        self.btn_iniciar.config(
            text="Acabar Simulação",
            bg="#ef4444",
            command=self.acabar_simulacao,
            state="normal"
        )
        self.btn_pausar.config(
            text="Retomar",
            bg="#10b981",
            command=self.pausar_simulacao,
            state="normal"
        )

    def _set_estado_bloqueado_botoes(self):
        """Estado bloqueado: simulação terminada."""
        self.btn_iniciar.config(
            text="Simulação Terminada",
            bg="#9ca3af",
            state="disabled"
        )
        self.btn_pausar.config(
            text="Pausar",
            bg="#9ca3af",
            state="disabled"
        )

    # -------------------- log --------------------

    def registar_evento(self, msg: str):
        """Adiciona mensagem ao log."""
        if self._a_fechar:
            return
        try:
            self.text_log.insert(tk.END, f"{msg}\n")
            self.text_log.see(tk.END)
            self.root.update_idletasks()
        except tk.TclError:
            pass

    # -------------------- UI loop --------------------

    def atualizar(self):
        """Atualiza a interface com dados atuais."""
        if self._a_fechar:
            return

        try:
            m = self.simulador.gestor.metricas
            metrics = m.calcular_metricas()

            # Tempo
            self.label_tempo.config(
                text=f"{self.simulador.tempo_atual}/{self.config['duracao']} min"
            )

            # Trânsito
            if self.simulador.gestor_transito:
                hora = self.simulador.gestor_transito.hora_atual
                self.label_hora.config(text=f"Hora: {hora:02d}:00")

                factor = self.simulador.gestor_transito.calcular_factor_hora(hora)
                if factor >= 1.8:
                    self.label_transito.config(text="Trânsito: RUSH!", fg="#ef4444")
                elif factor >= 1.3:
                    self.label_transito.config(text="Trânsito: Moderado", fg="#f59e0b")
                elif factor < 1.0:
                    self.label_transito.config(text="Trânsito: Fluido", fg="#10b981")
                else:
                    self.label_transito.config(text="Trânsito: Normal", fg="#6b7280")

            # Frota
            veiculos = list(self.simulador.gestor.veiculos.values())
            total = len(veiculos)

            disponiveis = sum(1 for v in veiculos if v.estado == EstadoVeiculo.DISPONIVEL)
            servico = sum(
                1 for v in veiculos
                if v.estado in (EstadoVeiculo.EM_DESLOCACAO, EstadoVeiculo.A_SERVICO)
            )
            recarga = sum(
                1 for v in veiculos
                if v.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER)
            )
            indisp = sum(1 for v in veiculos if v.estado == EstadoVeiculo.INDISPONIVEL)

            self.card_disponiveis.config(text=f"{disponiveis}/{total}")
            self.card_servico.config(text=str(servico))
            self.card_recarga.config(text=str(recarga))
            self.card_indisp.config(text=str(indisp))

            # Pedidos
            pedidos_ativos = [
                p for p in self.simulador.gestor.pedidos_pendentes
                if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)
            ]
            self.gestor_pedidos_visuais.atualizar(pedidos_ativos)

            # Métricas
            total_pedidos = metrics["pedidos_servicos"] + metrics["pedidos_rejeitados"]
            self.metricas_labels["pedidos"].config(
                text=f"{metrics['pedidos_servicos']}/{total_pedidos}"
            )
            self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
            self.metricas_labels["tempo_resp"].config(
                text=f"{metrics['tempo_medio_resposta']:.1f}m"
            )
            self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
            self.metricas_labels["dead_mileage"].config(
                text=f"{metrics['perc_km_vazio']:.1f}%"
            )
            self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")
            self.metricas_labels["emissoes"].config(
                text=f"{metrics['emissoes_totais']:.1f}kg"
            )

            # Falhas
            if self.simulador.gestor_falhas:
                estado = self.simulador.gestor_falhas.obter_estado_estacoes()
                total_est = (
                    estado["estacoes_recarga"]["total"]
                    + estado["postos_abastecimento"]["total"]
                )
                online_est = (
                    estado["estacoes_recarga"]["online"]
                    + estado["postos_abastecimento"]["online"]
                )
                self.metricas_labels["estacoes"].config(text=f"{online_est}/{total_est}")

            # Ride Sharing
            if "ride_sharing" in self.metricas_labels and self.simulador.gestor_ride_sharing:
                stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
                self.metricas_labels["ride_sharing"].config(text=str(stats["grupos_criados"]))

            # Mapa
            self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos_ativos)

        except Exception as e:
            print(f"Erro ao atualizar UI: {e}")

        # Reagenda
        if not self._a_fechar:
            self.ui_scheduler.schedule(self.intervalo_atualizacao, self.atualizar)

    # -------------------- simulation controls --------------------

    def executar_simulacao(self):
        """Inicia ou reinicia a simulação."""
        if self._a_fechar or self.simulacao_bloqueada:
            return

        # Se já terminou, reinicia
        if self.simulador.tempo_atual >= self.config["duracao"]:
            self.reiniciar_simulacao()

        self.simulacao_ativa = True
        self._set_estado_em_execucao_botoes()

        self.registar_evento(f"▶️ Simulação iniciada ({self.velocidade}x)")
        self.executar_passo()

    def acabar_simulacao(self):
        """Termina a simulação definitivamente."""
        if self._a_fechar:
            return

        self.simulacao_ativa = False
        self.step_scheduler.cancel()
        self.simulacao_bloqueada = True

        self.registar_evento("SIMULAÇÃO TERMINADA PELO UTILIZADOR")

        # Mostra resultados
        m = self.simulador.gestor.metricas
        metricas = m.calcular_metricas_extensas(self.simulador.gestor.veiculos)
        self.mostrar_popup_resultados(metricas)

        # Bloqueia controles
        self._set_estado_bloqueado_botoes()

    def executar_passo(self):
        """Executa um ou mais passos da simulação."""
        if self._a_fechar or not self.simulacao_ativa:
            return

        # Verifica se terminou
        if self.simulador.tempo_atual >= self.config["duracao"]:
            self.finalizar_simulacao()
            return

        # Executa passos de acordo com a velocidade
        for _ in range(self.velocidade):
            if not self.simulacao_ativa or self.simulador.tempo_atual >= self.config["duracao"]:
                break
            self.executar_passo_individual()

        # Reagenda se ainda ativo
        if self.simulacao_ativa and self.simulador.tempo_atual < self.config["duracao"]:
            self.step_scheduler.schedule(self.intervalo_atualizacao, self.executar_passo)

    def executar_passo_individual(self):
        """Executa um único passo da simulação."""
        if self._a_fechar or not self.simulacao_ativa:
            return

        # Atualiza trânsito
        if self.simulador.gestor_transito:
            self.simulador.gestor_transito.atualizar_transito(self.simulador.tempo_atual)

        # Simula falhas
        if self.simulador.gestor_falhas and self.simulador.tempo_atual % 5 == 0:
            falhas = self.simulador.gestor_falhas.simular_falha_aleatoria(
                self.simulador.tempo_atual
            )
            for est_id in falhas:
                self.registar_evento(
                    f"⚠️ [t={self.simulador.tempo_atual}] {est_id} OFFLINE"
                )

        # Processa simulação
        self.simulador.processar_pedidos_novos()
        self.simulador.atribuir_pedidos_pendentes()
        self.simulador.mover_veiculos()
        self.simulador.verificar_conclusao_pedidos()
        self.simulador.verificar_recargas()

        # Reposicionamento
        if self.simulador.tempo_atual % 5 == 0 and self.config.get("reposicionamento", False):
            pedidos_futuros = [p for _, _, _, p in self.simulador.fila_pedidos]
            self.simulador.gestor.reposicionar_veiculos(
                self.simulador.tempo_atual, pedidos_futuros
            )

        self.simulador.tempo_atual += 1

    def pausar_simulacao(self):
        """Pausa ou retoma a simulação."""
        if self._a_fechar or self.simulacao_bloqueada:
            return

        if self.simulacao_ativa:
            # Pausar
            self.simulacao_ativa = False
            self.step_scheduler.cancel()
            self._set_estado_pausado_botoes()
            self.registar_evento("PAUSADA")
        else:
            # Retomar
            self.simulacao_ativa = True
            self._set_estado_em_execucao_botoes()
            self.registar_evento("RETOMADA")
            self.executar_passo()

    # -------------------- final results popup --------------------

    def finalizar_simulacao(self):
        """Fim natural da simulação (tempo esgotado)."""
        if self._a_fechar:
            return

        self.simulacao_ativa = False
        self.step_scheduler.cancel()
        self._set_estado_bloqueado_botoes()
        self.simulacao_bloqueada = True

        m = self.simulador.gestor.metricas
        metricas = m.calcular_metricas_extensas(self.simulador.gestor.veiculos)

        self.registar_evento("\n" + "=" * 40)
        self.registar_evento("SIMULAÇÃO CONCLUÍDA")
        self.registar_evento("=" * 40)
        self.registar_evento(f"Servidos: {metricas['pedidos_servicos']}")
        self.registar_evento(f"Rejeitados: {metricas['pedidos_rejeitados']}")
        self.registar_evento(f"Taxa: {metricas['taxa_sucesso']:.1f}%")

        self.mostrar_popup_resultados(metricas)

    def mostrar_popup_resultados(self, metricas):
        """Mostra popup com resultados finais."""
        popup = tk.Toplevel(self.root)
        popup.title("Resultados da Simulação")
        popup.geometry("520x640")
        popup.configure(bg="#ffffff")
        popup.transient(self.root)
        popup.resizable(False, False)

        # Header
        tk.Frame(popup, bg="#10b981", height=64).pack(fill="x")
        tk.Label(
            popup,
            text="Resultados da Simulação",
            bg="#10b981",
            fg="#ffffff",
            font=("Inter", 16, "bold"),
        ).place(x=260, y=22, anchor="center")

        # Content
        content = tk.Frame(popup, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=20, pady=16)

        def section(title: str):
            tk.Label(
                content,
                text=title,
                bg="#ffffff",
                fg="#111827",
                font=("Inter", 11, "bold"),
            ).pack(anchor="w", pady=(10, 6))

        def row(label: str, value: str):
            r = tk.Frame(content, bg="#ffffff")
            r.pack(fill="x", pady=2)
            tk.Label(
                r, text=label, bg="#ffffff", fg="#6b7280", font=("Inter", 9)
            ).pack(side="left")
            tk.Label(
                r, text=value, bg="#ffffff", fg="#111827", font=("Inter", 9, "bold")
            ).pack(side="right")

        total_pedidos = metricas["pedidos_servicos"] + metricas["pedidos_rejeitados"]

        section("Resumo")
        row("Pedidos atendidos", f"{metricas['pedidos_servicos']}/{total_pedidos}")
        row("Taxa de sucesso", f"{metricas['taxa_sucesso']:.1f}%")
        row("Tempo médio de resposta", f"{metricas['tempo_medio_resposta']:.1f} min")

        section("⚙️ Eficiência Operacional")
        row("Km totais", f"{metricas['km_totais']:.1f} km")
        row("Dead mileage", f"{metricas['perc_km_vazio']:.1f}%")
        row("Custo total", f"€{metricas['custo_total']:.2f}")
        row("Custo por km", f"€{metricas.get('custo_por_km', 0.0):.3f}/km")
        row(
            "Custo por pedido servido",
            f"€{metricas.get('custo_por_pedido_servico', 0.0):.2f}",
        )

        section("Impacto Ambiental")
        row("Emissões CO₂", f"{metricas['emissoes_totais']:.2f} kg")
        row("Emissões por km", f"{metricas.get('emissao_por_km', 0.0):.4f} kg/km")

        dead = metricas.get("dead_detail", {})
        top_dead = dead.get("top_dead_mileage", [])
        top_km = dead.get("top_km", [])

        if top_dead or top_km:
            section("Rankings (Top 3)")
            if top_dead:
                row(
                    "Mais km vazio",
                    ", ".join([f"{vid}({km:.1f})" for vid, km in top_dead]),
                )
            if top_km:
                row(
                    "Mais km totais", ", ".join([f"{vid}({km:.1f})" for vid, km in top_km])
                )

        # Botão fechar
        tk.Button(
            popup,
            text="Fechar",
            command=popup.destroy,
            bg="#3b82f6",
            fg="#ffffff",
            font=("Inter", 9, "bold"),
            relief="flat",
            padx=30,
            pady=8,
            cursor="hand2",
        ).pack(pady=14)

    # -------------------- reset --------------------

    def reiniciar_simulacao(self):
        """Reinicia a simulação do zero."""
        if self.simulacao_bloqueada:
            return

        self.simulador.tempo_atual = 0
        self.simulador.gestor.pedidos_pendentes = []
        self.simulador.gestor.pedidos_concluidos = []

        # Restaura fila de pedidos
        self.simulador.fila_pedidos = []
        for pedido in self.simulador.pedidos_todos:
            pedido.estado = EstadoPedido.PENDENTE
            pedido.veiculo_atribuido = None
            heapq.heappush(
                self.simulador.fila_pedidos,
                (pedido.instante_pedido, -pedido.prioridade, pedido.id_pedido, pedido),
            )

        # Restaura veículos
        for v in self.simulador.gestor.veiculos.values():
            v.estado = EstadoVeiculo.DISPONIVEL
            v.rota = []
            v.indice_rota = 0
            v.id_pedido_atual = None
            v.km_total = 0
            v.km_sem_passageiros = 0
            v.tempo_ocupado_ate = 0
            v.autonomia_km = v.autonomiaMax_km

        # Restaura métricas
        self.simulador.gestor.metricas = Metricas()
        self.gestor_pedidos_visuais.limpar()
        
        # Reseta bloqueio
        self.simulacao_bloqueada = False
        self._set_estado_inicial_botoes()
        
        self.registar_evento("Simulação reiniciada")

    def iniciar(self):
        """Inicia o loop principal da interface."""
        self.root.mainloop()