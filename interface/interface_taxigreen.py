"""
Interface Principal TaxiGreen
Responsabilidade: Lógica de controlo da simulação e gestão de eventos
"""

import tkinter as tk
import heapq
from interface.interface_mapa import InterfaceMapa
from interface.interface_componentes import ComponentesUI
from modelo.pedidos import EstadoPedido
from modelo.veiculos import EstadoVeiculo
from gestao.metricas import Metricas


class InterfaceTaxiGreen:
    """
    Controlador principal da interface.
    Gere a simulação e atualiza os componentes visuais.
    """

    def __init__(self, simulador, config: dict):
        self.simulador = simulador
        self.config = config
        self.simulacao_ativa = False
        self.velocidade = config.get('velocidade', 1)
        self.intervalo_atualizacao = self.calcular_intervalo(self.velocidade)
        
        # Criação da janela principal
        self.root = tk.Tk()
        self.root.title("TaxiGreen Simulator")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f9fafb")
        self.root.minsize(1200, 700)
        
        # Inicializa componentes UI
        self.criar_interface()
        
        # Agenda primeira atualização
        self.root.after(self.intervalo_atualizacao, self.atualizar)

    def calcular_intervalo(self, velocidade):
        """Calcula intervalo de atualização baseado na velocidade."""
        intervalos = {1: 1000, 2: 500, 5: 200, 10: 100}
        return intervalos.get(velocidade, 1000)

    def criar_interface(self):
        """Cria toda a estrutura da interface."""
        # ===== FRAME ESQUERDO: MAPA =====
        frame_mapa = tk.Frame(self.root, bg="#f9fafb")
        frame_mapa.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.mapa = InterfaceMapa(
            frame_mapa, 
            self.simulador.gestor.grafo, 
            width=900, height=700
        )

        # ===== FRAME DIREITO: SIDEBAR =====
        frame_direita = tk.Frame(self.root, bg="#ffffff", width=400)
        frame_direita.pack(side="right", fill="y", padx=(0, 10), pady=10)
        frame_direita.pack_propagate(False)

        # Container com scroll
        canvas_scroll = tk.Canvas(frame_direita, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_direita, orient="vertical", command=canvas_scroll.yview)
        self.frame_conteudo = tk.Frame(canvas_scroll, bg="#ffffff")

        self.frame_conteudo.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )

        canvas_scroll.create_window((0, 0), window=self.frame_conteudo, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        # ===== CRIA COMPONENTES UI =====
        componentes = ComponentesUI(self.frame_conteudo, self.config)
        
        # Header
        widgets_header = componentes.criar_header(self.frame_conteudo)
        self.label_tempo = widgets_header['label_tempo']
        self.label_hora = widgets_header['label_hora']
        self.label_transito = widgets_header['label_transito']
        
        # Painel Estado
        componentes.criar_painel_estado(
            self.frame_conteudo, 
            len(self.simulador.fila_pedidos)
        )
        
        # Frota
        widgets_frota = componentes.criar_secao_frota(self.frame_conteudo)
        self.label_disponiveis = widgets_frota['label_disponiveis']
        self.label_ocupados = widgets_frota['label_ocupados']
        self.label_recarregar = widgets_frota['label_recarregar']
        
        # Métricas
        self.metricas_labels = componentes.criar_secao_metricas(self.frame_conteudo)
        
        # Pedidos
        self.list_pedidos = componentes.criar_secao_pedidos(self.frame_conteudo)
        
        # Eventos
        self.text_log = componentes.criar_secao_eventos(self.frame_conteudo)

        # ===== BOTÕES FIXOS (fora do scroll) =====
        frame_botoes_fixo = tk.Frame(frame_direita, bg="#ffffff")
        frame_botoes_fixo.pack(side="bottom", fill="x", before=canvas_scroll)
        
        botoes = componentes.criar_botoes(frame_botoes_fixo, self.velocidade)
        self.btn_iniciar = botoes['btn_iniciar']
        self.btn_pausar = botoes['btn_pausar']
        
        # Conecta comandos
        self.btn_iniciar.config(command=self.executar_simulacao)
        self.btn_pausar.config(command=self.pausar_simulacao)

    # ========================================
    # MÉTODOS UTILITÁRIOS
    # ========================================

    def registar_evento(self, msg: str):
        """Adiciona mensagem ao log de eventos."""
        self.text_log.insert(tk.END, f"{msg}\n")
        self.text_log.see(tk.END)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def mostrar_pedido(self, pedido):
        """Adiciona pedido à lista visual."""
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino}"
        items = list(self.list_pedidos.get(0, tk.END))
        if display not in items:
            self.list_pedidos.insert(tk.END, display)
        self.mapa.desenhar_pedido(pedido)

    def remover_pedido_visual(self, pedido):
        """Remove pedido da lista visual."""
        display = f"{pedido.id_pedido}: {pedido.posicao_inicial} → {pedido.posicao_destino}"
        items = list(self.list_pedidos.get(0, tk.END))
        if display in items:
            self.list_pedidos.delete(items.index(display))
        self.mapa.remover_pedido(pedido)

    # ========================================
    # LOOP DE ATUALIZAÇÃO
    # ========================================

    def atualizar(self):
        """Atualização periódica da interface (chamada a cada intervalo)."""
        m = self.simulador.gestor.metricas
        metrics = m.calcular_metricas()

        # === TEMPO ===
        self.label_tempo.config(
            text=f"Tempo: {self.simulador.tempo_atual}/{self.config['duracao']} min"
        )

        # === HORA E TRÂNSITO ===
        if self.simulador.gestor_transito:
            hora = self.simulador.gestor_transito.hora_atual
            self.label_hora.config(text=f"Hora: {hora:02d}:00")

            factor = self.simulador.gestor_transito.calcular_factor_hora(hora)
            if factor >= 1.8:
                self.label_transito.config(text="Trânsito: RUSH HOUR!", fg="#ef4444")
            elif factor >= 1.3:
                self.label_transito.config(text="Trânsito: Moderado", fg="#f59e0b")
            elif factor < 1.0:
                self.label_transito.config(text="Trânsito: Fluido", fg="#10b981")
            else:
                self.label_transito.config(text="Trânsito: Normal", fg="#6b7280")

        # === ESTADO DA FROTA ===
        disponiveis = sum(
            1 for v in self.simulador.gestor.veiculos.values()
            if v.estado == EstadoVeiculo.DISPONIVEL
        )
        ocupados = sum(
            1 for v in self.simulador.gestor.veiculos.values()
            if v.estado in (EstadoVeiculo.EM_DESLOCACAO, EstadoVeiculo.A_SERVICO)
        )
        a_recarregar = sum(
            1 for v in self.simulador.gestor.veiculos.values()
            if v.estado in (EstadoVeiculo.A_CARREGAR, EstadoVeiculo.A_ABASTECER)
        )

        self.label_disponiveis.config(text=f"Disponíveis: {disponiveis}")
        self.label_ocupados.config(text=f"Ocupados: {ocupados}")
        self.label_recarregar.config(text=f"A recarregar: {a_recarregar}")

        # === MÉTRICAS ===
        total = metrics['pedidos_servicos'] + metrics['pedidos_rejeitados']
        self.metricas_labels["pedidos"].config(text=f"{metrics['pedidos_servicos']}/{total}")
        self.metricas_labels["taxa"].config(text=f"{metrics['taxa_sucesso']:.0f}%")
        self.metricas_labels["km"].config(text=f"{metrics['km_totais']:.0f}")
        self.metricas_labels["custo"].config(text=f"€{metrics['custo_total']:.0f}")
        self.metricas_labels["dead_mileage"].config(text=f"{metrics['perc_km_vazio']:.1f}%")
        self.metricas_labels["emissoes"].config(text=f"{metrics['emissoes_totais']:.1f}kg")
        self.metricas_labels["tempo_resp"].config(text=f"{metrics['tempo_medio_resposta']:.1f}m")

        # Estações
        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            total_est = estado['estacoes_recarga']['total'] + estado['postos_abastecimento']['total']
            online_est = estado['estacoes_recarga']['online'] + estado['postos_abastecimento']['online']
            self.metricas_labels["estacoes"].config(text=f"{online_est}/{total_est}")
        else:
            self.metricas_labels["estacoes"].config(text="N/A")

        # Ride Sharing
        if self.config.get('ride_sharing', False) and self.simulador.gestor_ride_sharing:
            stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
            self.metricas_labels["ride_sharing"].config(text=f"{stats['grupos_criados']}")

        # === MAPA ===
        estacoes_offline = set()
        if self.simulador.gestor_falhas:
            todas = (
                self.simulador.gestor_falhas.obter_estacoes_recarga() +
                self.simulador.gestor_falhas.obter_postos_abastecimento()
            )
            for est_id in todas:
                no = self.simulador.gestor.grafo.nos[est_id]
                if not no.disponivel:
                    estacoes_offline.add(est_id)
            self.mapa.desenhar_nos(estacoes_offline)

        pedidos = [
            p for p in self.simulador.gestor.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)
        ]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        # Agenda próxima atualização
        try:
            self.root.after(self.intervalo_atualizacao, self.atualizar)
        except tk.TclError:
            pass

    # ========================================
    # CONTROLO DA SIMULAÇÃO
    # ========================================

    def executar_simulacao(self):
        """Inicia a simulação."""
        if self.simulador.tempo_atual >= self.config['duracao']:
            self.reiniciar_simulacao()

        self.simulacao_ativa = True
        self.registar_evento(
            f"🚀 Simulação iniciada com {self.config['algoritmo'].upper()} a {self.velocidade}x"
        )
        self.executar_passo()

    def executar_passo(self):
        """Executa múltiplos passos baseado na velocidade."""
        if not self.simulacao_ativa or self.simulador.tempo_atual > self.config['duracao']:
            if self.simulador.tempo_atual > self.config['duracao']:
                self.finalizar_simulacao()
            return

        # Executa N passos por iteração
        passos = self.velocidade
        for _ in range(passos):
            if self.simulador.tempo_atual > self.config['duracao']:
                break
            self.executar_passo_individual()

    def executar_passo_individual(self):
        """Executa um único passo da simulação (1 minuto)."""
        # Trânsito
        if self.simulador.gestor_transito:
            self.simulador.gestor_transito.atualizar_transito(self.simulador.tempo_atual)

        # Falhas (a cada 5 minutos)
        if self.simulador.gestor_falhas and self.simulador.tempo_atual % 5 == 0:
            falhas = self.simulador.gestor_falhas.simular_falha_aleatoria(self.simulador.tempo_atual)
            for est_id in falhas:
                self.registar_evento(f"[t={self.simulador.tempo_atual}] ⚠️ FALHA: {est_id} OFFLINE")

        # Processamento da simulação
        self.simulador.processar_pedidos_novos()
        self.simulador.atribuir_pedidos_pendentes()
        self.simulador.mover_veiculos()
        self.simulador.verificar_conclusao_pedidos()
        self.simulador.verificar_recargas()

        # Reposicionamento (se ativo, a cada 5 minutos)
        if self.simulador.tempo_atual % 5 == 0 and self.config.get('reposicionamento', False):
            pedidos_futuros = [p for _, _, _, p in self.simulador.fila_pedidos]
            reposicionamentos = self.simulador.gestor.reposicionar_veiculos(
                self.simulador.tempo_atual, pedidos_futuros
            )
            if reposicionamentos:
                for vid, origem, destino in reposicionamentos:
                    self.registar_evento(
                        f"[t={self.simulador.tempo_atual}] REPOS: {vid} {origem}→{destino}"
                    )

        # Atualiza mapa
        pedidos = [
            p for p in self.simulador.gestor.pedidos_pendentes
            if p.estado in (EstadoPedido.PENDENTE, EstadoPedido.ATRIBUIDO, EstadoPedido.EM_EXECUCAO)
        ]
        self.mapa.atualizar(self.simulador.gestor.veiculos, pedidos)

        # Avança tempo
        self.simulador.tempo_atual += 1
        
        # Agenda próximo passo
        self.root.after(self.intervalo_atualizacao, self.executar_passo)

    def pausar_simulacao(self):
        """Pausa/retoma simulação."""
        if self.simulacao_ativa:
            self.simulacao_ativa = False
            self.btn_pausar.config(text="▶ Retomar", bg="#10b981")
            self.registar_evento("⏸ Simulação PAUSADA")
        else:
            self.simulacao_ativa = True
            self.btn_pausar.config(text="⏸ Pausar", bg="#ef4444")
            self.registar_evento("▶ Simulação RETOMADA")
            self.executar_passo()

    def finalizar_simulacao(self):
        """Finaliza simulação e mostra resultados."""
        self.simulacao_ativa = False
        metricas = self.simulador.gestor.metricas.calcular_metricas()

        # Log final
        self.registar_evento("\n" + "="*50)
        self.registar_evento(" SIMULAÇÃO TERMINADA")
        self.registar_evento("="*50)
        self.registar_evento(f"✓ Pedidos servidos: {metricas['pedidos_servicos']}")
        self.registar_evento(f"✗ Pedidos rejeitados: {metricas['pedidos_rejeitados']}")
        self.registar_evento(f"Taxa de sucesso: {metricas['taxa_sucesso']}%")
        self.registar_evento(f"Tempo médio: {metricas['tempo_medio_resposta']:.1f} min")
        self.registar_evento(f"Custo total: €{metricas['custo_total']:.2f}")
        self.registar_evento(f"Emissões: {metricas['emissoes_totais']:.2f} kg CO₂")
        self.registar_evento(f"Km totais: {metricas['km_totais']:.2f} km")
        self.registar_evento(f"Dead mileage: {metricas['perc_km_vazio']:.1f}%")

        # Estatísticas extras
        if self.simulador.gestor_falhas:
            estado = self.simulador.gestor_falhas.obter_estado_estacoes()
            self.registar_evento("\n--- ESTATÍSTICAS DE FALHAS ---")
            self.registar_evento(f"Total eventos: {estado['total_falhas_historico']}")

        if self.simulador.gestor_ride_sharing:
            stats = self.simulador.gestor_ride_sharing.obter_estatisticas()
            if stats['grupos_criados'] > 0:
                self.registar_evento("\n--- RIDE SHARING ---")
                self.registar_evento(f"Grupos criados: {stats['grupos_criados']}")
                self.registar_evento(f"Pedidos agrupados: {stats['pedidos_agrupados']}")
                self.registar_evento(f"Economia total: {stats['economia_total_km']:.1f} km")

        # Popup de resultados
        self.mostrar_popup_resultados(metricas)

    def mostrar_popup_resultados(self, metricas):
        """Mostra popup com resultados finais."""
        if hasattr(self, '_popup_aberto') and self._popup_aberto:
            return
        self._popup_aberto = True

        popup = tk.Toplevel(self.root)
        popup.title("Simulação Concluída")
        popup.geometry("500x650")
        popup.configure(bg="#ffffff")
        popup.transient(self.root)

        popup.update_idletasks()
        try:
            popup.grab_set()
        except:
            pass

        # Header
        header = tk.Frame(popup, bg="#10b981", height=80)
        header.pack(fill="x")
        tk.Label(
            header, text="✓ Simulação Concluída",
            bg="#10b981", fg="#ffffff",
            font=("Inter", 18, "bold")
        ).pack(pady=25)

        # Configuração
        config_frame = tk.Frame(popup, bg="#f9fafb")
        config_frame.pack(fill="x", padx=30, pady=(20, 10))

        tk.Label(
            config_frame, text="Configuração",
            bg="#f9fafb", fg="#6b7280",
            font=("Inter", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        config_info = [
            f"Algoritmo: {self.config['algoritmo'].upper()}",
            f"Duração: {self.config['duracao']} min",
            f"Velocidade: {self.velocidade}x",
        ]

        for info in config_info:
            tk.Label(
                config_frame, text=f"• {info}",
                bg="#f9fafb", fg="#374151",
                font=("Inter", 9)
            ).pack(anchor="w", padx=10)

        # Resultados
        content = tk.Frame(popup, bg="#ffffff")
        content.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        tk.Label(
            content, text="Resultados",
            bg="#ffffff", fg="#111827",
            font=("Inter", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        resultados = [
            ("Pedidos Atendidos", f"{metricas['pedidos_servicos']}/{metricas['pedidos_servicos'] + metricas['pedidos_rejeitados']}"),
            ("Taxa de Sucesso", f"{metricas['taxa_sucesso']:.1f}%"),
            ("Tempo Médio", f"{metricas['tempo_medio_resposta']:.1f} min"),
            ("Custo Total", f"€{metricas['custo_total']:.2f}"),
            ("Emissões CO₂", f"{metricas['emissoes_totais']:.1f} kg"),
            ("Km Totais", f"{metricas['km_totais']:.1f} km"),
            ("Dead Mileage", f"{metricas['perc_km_vazio']:.1f}%"),
        ]

        for label, valor in resultados:
            row = tk.Frame(content, bg="#ffffff")
            row.pack(fill="x", pady=5)
            tk.Label(
                row, text=label + ":",
                bg="#ffffff", fg="#6b7280",
                font=("Inter", 10)
            ).pack(side="left")
            tk.Label(
                row, text=valor,
                bg="#ffffff", fg="#111827",
                font=("Inter", 10, "bold")
            ).pack(side="right")

        def fechar_popup():
            self._popup_aberto = False
            popup.destroy()

        tk.Button(
            popup, text="Fechar",
            command=fechar_popup,
            bg="#3b82f6", fg="#ffffff",
            font=("Inter", 11, "bold"),
            relief="flat", padx=40, pady=12,
            cursor="hand2"
        ).pack(pady=20)

        popup.protocol("WM_DELETE_WINDOW", fechar_popup)

    def reiniciar_simulacao(self):
        """Reinicia simulação para o estado inicial."""
        self._popup_aberto = False
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
            v.km_sem_passageiros = 0.0
            v.id_pedido_atual = None
            v.tempo_ocupado_ate = 0
        
        self.simulador.gestor.metricas = Metricas()
        self.list_pedidos.delete(0, tk.END)
        self.registar_evento("Simulação reiniciada")

    def iniciar(self):
        """Inicia loop GUI."""
        self.root.mainloop()