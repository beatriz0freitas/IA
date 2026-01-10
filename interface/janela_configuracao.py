"""
Janelas de configuração pré-simulação para TaxiGreen.
Separadas em duas etapas: Simulação e Pedidos/Features.

Revisão UI:
- Remove bordas/retângulos pretos (relief/bd) -> tudo “flat”, como a interface principal
- Usa cores consistentes com a UI principal (verde/azul + backgrounds claros)
- Mantém layout compacto (2 colunas + combobox)
- Footer fixo com botões
- Bug fix: checkbox de Trânsito não deve chamar toggle_falhas_config
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


# =========================
# Paleta (alinhada com UI principal)
# =========================
_BG_APP = "#f3f4f6"       # igual a interface_taxigreen.py
_BG_CARD = "#ffffff"
_BG_MUTED = "#f9fafb"
_BORDER = "#e5e7eb"
_TEXT = "#111827"
_TEXT_MUTED = "#6b7280"
_GREEN = "#10b981"
_BLUE = "#3b82f6"
_GRAY_BTN = "#64748b"


def _font(size=10, weight="normal"):
    # Mantém Inter (se existir) mas com fallback automático do Tk
    return ("Inter", size, weight)


class JanelaConfiguracao:
    """
    Janela 1: Configuração da Simulação
    Define parâmetros base: duração, hora inicial, algoritmo, estratégia, trânsito, falhas, velocidade.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("TaxiGreen - Configuração da Simulação")
        self.root.geometry("720x720")
        self.root.configure(bg=_BG_APP)
        self.root.resizable(False, False)

        self.config = {}
        self.continuar = False

        self._setup_ttk()
        self.criar_interface()
        self.centrar_janela()

    def _setup_ttk(self):
        """ttk leve para Combobox + aparência consistente."""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Combobox mais “clean”
        style.configure("TCombobox", padding=6)

        # Remove realces “pretos” típicos
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", _BG_CARD)],
            background=[("readonly", _BG_CARD)],
            foreground=[("readonly", "#374151")],
        )

    def centrar_janela(self):
        """Centra janela no ecrã."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ---------- UI primitives (flat, sem bordas pretas) ----------
    def _separador(self, parent, pady=10, padx=18):
        tk.Frame(parent, bg=_BORDER, height=1).pack(fill="x", padx=padx, pady=pady)

    def _titulo(self, parent, text: str):
        tk.Label(
            parent,
            text=text,
            bg=_BG_APP,
            fg=_TEXT,
            font=_font(size=18, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(14, 6))

    def _subtitulo(self, parent, text: str):
        tk.Label(
            parent,
            text=text,
            bg=_BG_APP,
            fg=_TEXT_MUTED,
            font=_font(size=10),
        ).pack(anchor="w", padx=18, pady=(0, 10))

    def _card(self, parent, accent: str | None = None):
        """
        Card flat:
        - sem relief/sem bd (evita “retângulos pretos”)
        - separador em cima com cor (accent) para associar visualmente
        """
        card = tk.Frame(parent, bg=_BG_CARD)
        card.pack(fill="x", padx=18, pady=8)

        # top accent line (como nos cards/indicadores do UI principal)
        if accent:
            tk.Frame(card, bg=accent, height=3).pack(fill="x")
        else:
            tk.Frame(card, bg=_BORDER, height=1).pack(fill="x")

        return card

    def _card_header(self, card, title: str, subtitle: str | None = None):
        header = tk.Frame(card, bg=_BG_CARD)
        header.pack(fill="x", padx=14, pady=(10, 6))

        tk.Label(
            header,
            text=title.upper(),
            bg=_BG_CARD,
            fg=_TEXT,
            font=_font(size=9, weight="bold"),
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                bg=_BG_CARD,
                fg=_TEXT_MUTED,
                font=_font(size=9),
            ).pack(anchor="w", pady=(2, 0))

        tk.Frame(card, bg=_BORDER, height=1).pack(fill="x", padx=14, pady=(0, 10))

    def _field_label(self, parent, text: str):
        tk.Label(
            parent,
            text=text,
            bg=parent["bg"],
            fg=_TEXT_MUTED,
            font=_font(size=9),
        ).pack(anchor="w")

    def _mini_panel(self, parent, accent: str | None = None):
        """
        Mini panel flat para sub-config:
        - fundo ligeiramente diferente
        - linha superior colorida
        """
        panel = tk.Frame(parent, bg=_BG_MUTED)
        panel.pack(fill="x", pady=(8, 0))
        if accent:
            tk.Frame(panel, bg=accent, height=2).pack(fill="x")
        else:
            tk.Frame(panel, bg=_BORDER, height=1).pack(fill="x")
        return panel

    # ---------- Main ----------
    def criar_interface(self):
        # Layout: topo com scroll + footer fixo
        body = tk.Frame(self.root, bg=_BG_APP)
        body.pack(side="top", fill="both", expand=True)

        footer = tk.Frame(self.root, bg=_BG_CARD)
        footer.pack(side="bottom", fill="x")
        self._separador(footer, pady=0, padx=0)  # linha superior do footer

        # Scroll area
        canvas = tk.Canvas(body, bg=_BG_APP, highlightthickness=0)
        scrollbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg=_BG_APP)

        frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        header = tk.Frame(frame_scroll, bg=_BG_APP)
        header.pack(fill="x")

        self._titulo(header, "Configuração da Simulação")
        self._subtitulo(header, "Define duração, hora inicial, algoritmo, estratégia, velocidade e features dinâmicas.")
        self._separador(header, pady=10)

        # =========================
        # Card: Tempo (accent azul)
        # =========================
        card_tempo = self._card(frame_scroll, accent=_BLUE)
        self._card_header(card_tempo, "Tempo", "Duração e hora inicial do trânsito")

        grid = tk.Frame(card_tempo, bg=_BG_CARD)
        grid.pack(fill="x", padx=14, pady=(0, 14))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Duração
        col0 = tk.Frame(grid, bg=_BG_CARD)
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._field_label(col0, "Duração da simulação")
        self.duracao_var = tk.IntVar(value=60)

        duracoes = [30, 60, 90, 120]
        dur_grid = tk.Frame(col0, bg=_BG_CARD)
        dur_grid.pack(fill="x", pady=(6, 0))

        for i, d in enumerate(duracoes):
            tk.Radiobutton(
                dur_grid,
                text=f"{d} min",
                variable=self.duracao_var,
                value=d,
                bg=_BG_CARD,
                fg="#374151",
                font=_font(size=10),
                selectcolor=_BG_MUTED,
                activebackground=_BG_CARD,
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 14), pady=2)

        # Hora
        col1 = tk.Frame(grid, bg=_BG_CARD)
        col1.grid(row=0, column=1, sticky="nsew")
        self._field_label(col1, "Hora inicial do trânsito")
        self.hora_tipo_var = tk.StringVar(value="aleatoria")

        hora_box = tk.Frame(col1, bg=_BG_CARD)
        hora_box.pack(fill="x", pady=(6, 0))

        tk.Radiobutton(
            hora_box,
            text="Aleatória (0–23h)",
            variable=self.hora_tipo_var,
            value="aleatoria",
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_hora_spinbox,
        ).pack(anchor="w", pady=2)

        row_escolher = tk.Frame(hora_box, bg=_BG_CARD)
        row_escolher.pack(fill="x", pady=2)

        tk.Radiobutton(
            row_escolher,
            text="Especificar",
            variable=self.hora_tipo_var,
            value="escolhida",
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_hora_spinbox,
        ).pack(side="left")

        # Spinbox "flat": sem relief/sem borda preta (bd=0) + highlight 0
        self.hora_spinbox = tk.Spinbox(
            row_escolher,
            from_=0,
            to=23,
            width=6,
            font=_font(size=10),
            state="disabled",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            highlightcolor=_BLUE,
            bg=_BG_MUTED,
        )
        self.hora_spinbox.pack(side="left", padx=(8, 4))
        tk.Label(row_escolher, text="h", bg=_BG_CARD, fg=_TEXT_MUTED, font=_font(size=10)).pack(side="left")

        # =========================
        # Card: Decisões (accent verde)
        # =========================
        card_dec = self._card(frame_scroll, accent=_GREEN)
        self._card_header(card_dec, "Decisões", "Procura de rotas e seleção de veículos")

        grid2 = tk.Frame(card_dec, bg=_BG_CARD)
        grid2.pack(fill="x", padx=14, pady=(0, 14))
        grid2.columnconfigure(0, weight=1)
        grid2.columnconfigure(1, weight=1)

        left = tk.Frame(grid2, bg=_BG_CARD)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = tk.Frame(grid2, bg=_BG_CARD)
        right.grid(row=0, column=1, sticky="nsew")

        self._field_label(left, "Algoritmo de procura")
        self.algoritmo_var = tk.StringVar(value="astar")
        self._algoritmos = [
            ("A* (A-Estrela) — ótimo e eficiente", "astar"),
            ("Greedy — rápido, mas não ótimo", "greedy"),
            ("UCS — ótimo, mas mais lento", "ucs"),
            ("BFS — não considera custos", "bfs"),
            ("DFS — exploratório", "dfs"),
        ]
        self._algoritmo_display = [t for (t, _) in self._algoritmos]
        self.cb_algoritmo = ttk.Combobox(left, values=self._algoritmo_display, state="readonly", height=6)
        self.cb_algoritmo.pack(fill="x", pady=(6, 0))
        self.cb_algoritmo.current(0)

        self._field_label(right, "Estratégia de seleção")
        self.estrategia_var = tk.StringVar(value="dead_mileage")
        self._estrategias = [
            ("Minimizar Dead Mileage", "dead_mileage"),
            ("Menor Distância", "menor_distancia"),
            ("Custo Composto", "custo_composto"),
            ("Equilibrada", "equilibrada"),
            ("Priorizar Elétricos", "priorizar_eletricos"),
        ]
        self._estrategia_display = [t for (t, _) in self._estrategias]
        self.cb_estrategia = ttk.Combobox(right, values=self._estrategia_display, state="readonly", height=6)
        self.cb_estrategia.pack(fill="x", pady=(6, 0))
        self.cb_estrategia.current(0)

        # =========================
        # Card: Execução (accent azul)
        # =========================
        card_exec = self._card(frame_scroll, accent=_BLUE)
        self._card_header(card_exec, "Execução", "Velocidade e features dinâmicas")

        grid3 = tk.Frame(card_exec, bg=_BG_CARD)
        grid3.pack(fill="x", padx=14, pady=(0, 14))
        grid3.columnconfigure(0, weight=1)
        grid3.columnconfigure(1, weight=1)

        col_v = tk.Frame(grid3, bg=_BG_CARD)
        col_v.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        col_f = tk.Frame(grid3, bg=_BG_CARD)
        col_f.grid(row=0, column=1, sticky="nsew")

        # Velocidade
        self._field_label(col_v, "Velocidade da simulação")
        self.velocidade_var = tk.IntVar(value=1)
        self._velocidades = [
            ("1x — Normal", 1),
            ("2x — Rápida", 2),
            ("5x — Muito rápida", 5),
            ("10x — Máxima", 10),
        ]
        self._velocidade_display = [t for (t, _) in self._velocidades]
        self.cb_velocidade = ttk.Combobox(col_v, values=self._velocidade_display, state="readonly", height=6)
        self.cb_velocidade.pack(fill="x", pady=(6, 0))
        self.cb_velocidade.current(0)
        self.cb_velocidade.bind("<<ComboboxSelected>>", self._on_velocidade_change)

        self.aviso_vel = tk.Label(
            col_v,
            text="Velocidades > 2x podem reduzir a precisão visual.",
            bg=_BG_CARD,
            fg=_TEXT_MUTED,
            font=_font(size=8),
            wraplength=280,
            justify="left",
        )
        self.aviso_vel.pack(anchor="w", pady=(8, 0))

        # Features
        self._field_label(col_f, "Features dinâmicas")
        self.transito_var = tk.BooleanVar(value=True)
        self.falhas_var = tk.BooleanVar(value=True)

        tk.Checkbutton(
            col_f,
            text="Trânsito dinâmico",
            variable=self.transito_var,
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
        ).pack(anchor="w", pady=(6, 2))

        tk.Checkbutton(
            col_f,
            text="Falhas em estações",
            variable=self.falhas_var,
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_falhas_config,
        ).pack(anchor="w", pady=2)

        # Sub-config (mini panel) com cor de falhas (usa azul ou verde? aqui uso azul suave)
        self.falhas_config_frame = self._mini_panel(col_f, accent=_BLUE)
        inner = tk.Frame(self.falhas_config_frame, bg=_BG_MUTED)
        inner.pack(fill="x", padx=10, pady=8)
        inner.columnconfigure(0, weight=1)

        tk.Label(
            inner,
            text="Probabilidade de falhas",
            bg=_BG_MUTED,
            fg=_TEXT_MUTED,
            font=_font(size=9),
        ).grid(row=0, column=0, sticky="w")

        self.prob_falha_var = tk.DoubleVar(value=0.08)
        self.prob_falha_spinbox = tk.Spinbox(
            inner,
            from_=0.0,
            to=0.30,
            increment=0.05,
            width=7,
            format="%.2f",
            textvariable=self.prob_falha_var,
            font=_font(size=9),
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            highlightcolor=_BLUE,
            bg=_BG_CARD,
        )
        self.prob_falha_spinbox.grid(row=0, column=1, padx=(10, 0), sticky="e")

        # Inicial: aplica toggle correto
        self.toggle_falhas_config()

        # =========================
        # Footer (botões)
        # =========================
        footer_inner = tk.Frame(footer, bg=_BG_CARD)
        footer_inner.pack(fill="x", padx=14, pady=12)

        tk.Label(
            footer_inner,
            text="Passo 1 de 2",
            bg=_BG_CARD,
            fg=_TEXT_MUTED,
            font=_font(size=9),
        ).pack(side="left")

        btns = tk.Frame(footer_inner, bg=_BG_CARD)
        btns.pack(side="right")

        tk.Button(
            btns,
            text="Cancelar",
            command=self.cancelar,
            bg=_GRAY_BTN,
            fg="#ffffff",
            font=_font(size=10, weight="bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btns,
            text="Continuar →",
            command=self.validar_e_continuar,
            bg=_GREEN,
            fg="#ffffff",
            font=_font(size=11, weight="bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=10,
        ).pack(side="left")

    # ---------- callbacks ----------
    def _on_velocidade_change(self, _evt=None):
        sel = self.cb_velocidade.get()
        for label, v in self._velocidades:
            if label == sel:
                self.velocidade_var.set(v)
                break

        if self.velocidade_var.get() > 2:
            self.aviso_vel.config(fg="#92400e")
        else:
            self.aviso_vel.config(fg=_TEXT_MUTED)

    def toggle_hora_spinbox(self):
        if self.hora_tipo_var.get() == "escolhida":
            self.hora_spinbox.config(state="normal")
        else:
            self.hora_spinbox.config(state="disabled")

    def toggle_falhas_config(self):
        if self.falhas_var.get():
            self.falhas_config_frame.pack(fill="x", pady=(8, 0))
        else:
            self.falhas_config_frame.pack_forget()

    def cancelar(self):
        self.continuar = False
        self.root.destroy()

    def _resolve_combobox_value(self, selected_label: str, options: list[tuple[str, str]]) -> str:
        for label, internal in options:
            if label == selected_label:
                return internal
        return options[0][1] if options else selected_label

    def validar_e_continuar(self):
        # Map combobox -> valor interno
        self.algoritmo_var.set(self._resolve_combobox_value(self.cb_algoritmo.get(), self._algoritmos))
        self.estrategia_var.set(self._resolve_combobox_value(self.cb_estrategia.get(), self._estrategias))
        self._on_velocidade_change()

        self.config = {
            "duracao": self.duracao_var.get(),
            "hora_tipo": self.hora_tipo_var.get(),
            "hora_escolhida": int(self.hora_spinbox.get()) if self.hora_tipo_var.get() == "escolhida" else None,
            "algoritmo": self.algoritmo_var.get(),
            "estrategia": self.estrategia_var.get(),
            "usar_transito": self.transito_var.get(),
            "usar_falhas": self.falhas_var.get(),
            "prob_falha": float(self.prob_falha_spinbox.get()) if self.falhas_var.get() else 0.0,
            "velocidade": int(self.velocidade_var.get()),
        }

        self.continuar = True
        self.root.destroy()

    def obter_config(self) -> Dict[str, Any]:
        return self.config


class JanelaFeatures:
    """
    Janela 2: Configuração de Features Avançadas
    (flat + cores consistentes)
    """

    def __init__(self, root):
        self.root = root
        self.root.title("TaxiGreen - Configuração de Features")
        self.root.geometry("720x620")
        self.root.configure(bg=_BG_APP)
        self.root.resizable(False, False)

        self.config = {}
        self.continuar = False

        self._setup_ttk()
        self.criar_interface()
        self.centrar_janela()

    def _setup_ttk(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", padding=6)

    def centrar_janela(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _separador(self, parent, pady=10, padx=18):
        tk.Frame(parent, bg=_BORDER, height=1).pack(fill="x", padx=padx, pady=pady)

    def _card(self, parent, accent: str | None = None):
        card = tk.Frame(parent, bg=_BG_CARD)
        card.pack(fill="x", padx=18, pady=8)
        tk.Frame(card, bg=(accent or _BORDER), height=(3 if accent else 1)).pack(fill="x")
        return card

    def _card_header(self, card, title: str, subtitle: str | None = None):
        header = tk.Frame(card, bg=_BG_CARD)
        header.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(header, text=title.upper(), bg=_BG_CARD, fg=_TEXT, font=_font(size=9, weight="bold")).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, bg=_BG_CARD, fg=_TEXT_MUTED, font=_font(size=9)).pack(anchor="w", pady=(2, 0))
        tk.Frame(card, bg=_BORDER, height=1).pack(fill="x", padx=14, pady=(0, 10))

    def _mini_panel(self, parent, accent: str | None = None):
        panel = tk.Frame(parent, bg=_BG_MUTED)
        if accent:
            tk.Frame(panel, bg=accent, height=2).pack(fill="x")
        else:
            tk.Frame(panel, bg=_BORDER, height=1).pack(fill="x")
        return panel

    def criar_interface(self):
        # Header
        header = tk.Frame(self.root, bg=_BG_APP)
        header.pack(fill="x")
        tk.Label(header, text="Configuração de Pedidos/Features", bg=_BG_APP, fg=_TEXT, font=_font(size=18, weight="bold")).pack(
            anchor="w", padx=18, pady=(14, 6)
        )
        tk.Label(header, text="Define otimizações e como os pedidos são gerados.", bg=_BG_APP, fg=_TEXT_MUTED, font=_font(size=10)).pack(
            anchor="w", padx=18, pady=(0, 10)
        )
        self._separador(header, pady=10)

        content = tk.Frame(self.root, bg=_BG_APP)
        content.pack(fill="both", expand=True)

        # Card otimizações (verde)
        card_opt = self._card(content, accent=_GREEN)
        self._card_header(card_opt, "Otimizações")

        self.reposicionamento_var = tk.BooleanVar(value=True)
        self.ride_sharing_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            card_opt,
            text="Reposicionamento Proativo",
            variable=self.reposicionamento_var,
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
        ).pack(anchor="w", padx=14, pady=2)

        tk.Checkbutton(
            card_opt,
            text="Ride Sharing",
            variable=self.ride_sharing_var,
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_ride_sharing_config,
        ).pack(anchor="w", padx=14, pady=2)

        self.ride_sharing_config_frame = self._mini_panel(card_opt, accent=_BLUE)
        inner_rs = tk.Frame(self.ride_sharing_config_frame, bg=_BG_MUTED)
        inner_rs.pack(fill="x", padx=10, pady=8)
        inner_rs.columnconfigure(0, weight=1)

        tk.Label(inner_rs, text="Raio de agrupamento (km):", bg=_BG_MUTED, fg=_TEXT_MUTED, font=_font(size=9)).grid(
            row=0, column=0, sticky="w", pady=3
        )
        self.raio_var = tk.DoubleVar(value=5.0)
        tk.Spinbox(
            inner_rs,
            from_=1.0,
            to=10.0,
            increment=0.5,
            textvariable=self.raio_var,
            width=8,
            font=_font(size=9),
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            highlightcolor=_BLUE,
            bg=_BG_CARD,
        ).grid(row=0, column=1, padx=(10, 0))

        tk.Label(inner_rs, text="Janela temporal (min):", bg=_BG_MUTED, fg=_TEXT_MUTED, font=_font(size=9)).grid(
            row=1, column=0, sticky="w", pady=3
        )
        self.janela_var = tk.IntVar(value=10)
        tk.Spinbox(
            inner_rs,
            from_=5,
            to=15,
            increment=1,
            textvariable=self.janela_var,
            width=8,
            font=_font(size=9),
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            highlightcolor=_BLUE,
            bg=_BG_CARD,
        ).grid(row=1, column=1, padx=(10, 0))

        # Card pedidos (azul)
        card_ped = self._card(content, accent=_BLUE)
        self._card_header(card_ped, "Geração de Pedidos")

        self.pedidos_tipo_var = tk.StringVar(value="demo")

        tk.Radiobutton(
            card_ped,
            text="Usar Pedidos Demo (30 pedidos pré-definidos)",
            variable=self.pedidos_tipo_var,
            value="demo",
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_pedidos_config,
        ).pack(anchor="w", padx=14, pady=2)

        tk.Radiobutton(
            card_ped,
            text="Gerar Pedidos Aleatórios",
            variable=self.pedidos_tipo_var,
            value="aleatorios",
            bg=_BG_CARD,
            fg="#374151",
            font=_font(size=10),
            selectcolor=_BG_MUTED,
            activebackground=_BG_CARD,
            command=self.toggle_pedidos_config,
        ).pack(anchor="w", padx=14, pady=2)

        self.pedidos_config_frame = self._mini_panel(card_ped, accent=_BLUE)
        inner_p = tk.Frame(self.pedidos_config_frame, bg=_BG_MUTED)
        inner_p.pack(fill="x", padx=10, pady=8)
        inner_p.columnconfigure(0, weight=1)

        tk.Label(inner_p, text="Número de pedidos:", bg=_BG_MUTED, fg=_TEXT_MUTED, font=_font(size=9)).grid(row=0, column=0, sticky="w")
        self.num_pedidos_var = tk.IntVar(value=25)
        tk.Spinbox(
            inner_p,
            from_=10,
            to=50,
            increment=5,
            textvariable=self.num_pedidos_var,
            width=7,
            font=_font(size=9),
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            highlightcolor=_BLUE,
            bg=_BG_CARD,
        ).grid(row=0, column=1, padx=(10, 0), sticky="e")

        # Footer fixo
        footer = tk.Frame(self.root, bg=_BG_CARD)
        footer.pack(side="bottom", fill="x")
        self._separador(footer, pady=0, padx=0)

        footer_inner = tk.Frame(footer, bg=_BG_CARD)
        footer_inner.pack(fill="x", padx=14, pady=12)

        tk.Label(footer_inner, text="Passo 2 de 2", bg=_BG_CARD, fg=_TEXT_MUTED, font=_font(size=9)).pack(side="left")

        btns = tk.Frame(footer_inner, bg=_BG_CARD)
        btns.pack(side="right")

        tk.Button(
            btns,
            text="← Voltar",
            command=self.voltar,
            bg=_GRAY_BTN,
            fg="#ffffff",
            font=_font(size=10, weight="bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btns,
            text="Iniciar Simulação",
            command=self.validar_e_iniciar,
            bg=_GREEN,
            fg="#ffffff",
            font=_font(size=11, weight="bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=10,
        ).pack(side="left")

        # init toggles
        self.toggle_ride_sharing_config()
        self.toggle_pedidos_config()

    def toggle_ride_sharing_config(self):
        if self.ride_sharing_var.get():
            self.ride_sharing_config_frame.pack(fill="x", padx=14, pady=(10, 12))
        else:
            self.ride_sharing_config_frame.pack_forget()

    def toggle_pedidos_config(self):
        if self.pedidos_tipo_var.get() == "aleatorios":
            self.pedidos_config_frame.pack(fill="x", padx=14, pady=(10, 12))
        else:
            self.pedidos_config_frame.pack_forget()

    def voltar(self):
        self.continuar = False
        self.root.destroy()

    def validar_e_iniciar(self):
        self.config = {
            "reposicionamento": self.reposicionamento_var.get(),
            "ride_sharing": self.ride_sharing_var.get(),
            "tipo_pedidos": self.pedidos_tipo_var.get(),
            "num_pedidos": self.num_pedidos_var.get() if self.pedidos_tipo_var.get() == "aleatorios" else 0,
        }

        if self.ride_sharing_var.get():
            self.config["raio_agrupamento"] = self.raio_var.get()
            self.config["janela_temporal"] = self.janela_var.get()

        self.continuar = True
        self.root.destroy()

    def obter_config(self) -> Dict[str, Any]:
        return self.config


# === FUNÇÃO PRINCIPAL ===
def obter_configuracoes_simulacao() -> Dict[str, Any]:
    """
    Executa as duas janelas de configuração sequencialmente.

    Returns:
        Dict com todas as configurações escolhidas ou None se cancelado.
    """
    import random

    root1 = tk.Tk()
    janela1 = JanelaConfiguracao(root1)
    root1.mainloop()

    if not janela1.continuar:
        return None

    config_simulacao = janela1.obter_config()

    root2 = tk.Tk()
    janela2 = JanelaFeatures(root2)
    root2.mainloop()

    if not janela2.continuar:
        return None

    config_features = janela2.obter_config()

    config_completa = {**config_simulacao, **config_features}

    if config_completa["hora_tipo"] == "aleatoria":
        config_completa["hora_inicial"] = random.randint(0, 23)
    else:
        config_completa["hora_inicial"] = config_completa["hora_escolhida"]

    del config_completa["hora_tipo"]
    del config_completa["hora_escolhida"]

    return config_completa