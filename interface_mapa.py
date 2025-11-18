"""
Interface do Mapa refatorizada - Visualização do grafo e entidades
"""

import tkinter as tk
from modelo.grafo import Grafo, TipoNo

NODE_RADIUS = 10
VEHICLE_HALF = 6
SCALE = 90
OFFSET_X = 500
OFFSET_Y = 250


class InterfaceMapa(tk.Canvas):
    """Canvas para visualizar o grafo urbano, veículos e pedidos"""

    def __init__(self, parent, grafo: Grafo, width=800, height=600):
        super().__init__(parent, bg="#f2fdf5", highlightthickness=0, 
                         width=width, height=height)
        self.grafo = grafo
        self.pack(expand=True, fill="both")
        
        self.veiculos_desenhados = {}  # id_veiculo → canvas_id
        self.pedidos_desenhados = {}   # id_pedido → (marker_id, text_id)
        self.pos_cache = {}            # id_no → (x, y) pixels

        self.desenhar_grafo()
        self.desenhar_legenda()

    def _pos(self, id_no: str) -> tuple:
        """Calcula posição em pixels de um nó (com cache)"""
        if id_no in self.pos_cache:
            return self.pos_cache[id_no]

        no = self.grafo.nos[id_no]
        x = no.posicaox * SCALE + OFFSET_X
        y = no.posicaoy * SCALE + OFFSET_Y
        self.pos_cache[id_no] = (x, y)
        return x, y

    def desenhar_arestas(self):
        """Desenha todas as arestas do grafo"""
        self.delete("arestas")

        for origem, arestas in self.grafo.adjacentes.items():
            x1, y1 = self._pos(origem)

            for aresta in arestas:
                # Evitar desenhar duas vezes (grafo não-direcionado)
                if origem < aresta.no_destino:
                    x2, y2 = self._pos(aresta.no_destino)
                    self.create_line(x1, y1, x2, y2, fill="#cfcfcf", 
                                   width=2, tags="arestas")

    def desenhar_nos(self):
        """Desenha todos os nós com cores de acordo com tipo"""
        self.delete("nos")

        cores_tipo = {
            TipoNo.RECOLHA_PASSAGEIROS: "#6fd673",
            TipoNo.ESTACAO_RECARGA: "#77bfff",
            TipoNo.POSTO_ABASTECIMENTO: "#ffb366"
        }

        for no in self.grafo.nos.values():
            x, y = self._pos(no.id_no)
            cor = cores_tipo.get(no.tipo, "#95a5a6")

            # Desenhar círculo do nó
            self.create_oval(x - NODE_RADIUS, y - NODE_RADIUS,
                            x + NODE_RADIUS, y + NODE_RADIUS,
                            fill=cor, outline="#333",
                            tags=("nos", f"no_{no.id_no}"))

            # Label do nó
            self.create_text(x, y - NODE_RADIUS - 10,
                           text=no.id_no, font=("Arial", 9, "bold"),
                           tags="nos")

    def desenhar_grafo(self):
        """Renderiza grafo completo (arestas + nós)"""
        self.desenhar_arestas()
        self.desenhar_nos()

    def desenhar_legenda(self, x=10, y=200):
        """Desenha legenda dos símbolos no canto esquerdo"""
        self.delete("legenda")

        legendas = [
            ("Zona de recolha", "#6fd673", "oval"),
            ("Estação de recarga", "#77bfff", "oval"),
            ("Posto de abastecimento", "#ffb366", "oval"),
            ("Veículo Elétrico", "#0077cc", "rect"),
            ("Veículo Combustão", "#cc7700", "rect"),
            ("Pedido ativo", "#9b59b6", "pin"),
        ]

        spacing = 26
        for i, (label, color, shape) in enumerate(legendas):
            yy = y + i * spacing

            if shape == "oval":
                self.create_oval(x, yy, x + 14, yy + 14,
                               fill=color, outline="black", tags="legenda")
            elif shape == "rect":
                self.create_rectangle(x, yy, x + 14, yy + 14,
                                    fill=color, outline="black", tags="legenda")
            elif shape == "pin":
                self.create_oval(x, yy, x + 12, yy + 12,
                               fill=color, outline="black", tags="legenda")

            self.create_text(x + 22, yy + 7, text=label, anchor="w",
                           font=("Arial", 9), tags="legenda")

    def desenhar_pedido(self, pedido):
        """Desenha marcador de pedido na origem"""
        pid = pedido.id_pedido

        # Remover desenho antigo se existir
        if pid in self.pedidos_desenhados:
            marker_id, text_id = self.pedidos_desenhados[pid]
            self.delete(marker_id)
            self.delete(text_id)

        x, y = self._pos(pedido.posicao_inicial)

        # Marcador roxo para o pedido
        marker = self.create_oval(x - 6, y - 6, x + 6, y + 6,
                                 fill="#9b59b6", outline="#4a235a",
                                 tags=("pedidos", f"pedido_{pid}"))

        text = self.create_text(x, y - 16,
                              text=pid, font=("Arial", 8, "bold"),
                              tags=("pedidos",))

        self.pedidos_desenhados[pid] = (marker, text)

    def remover_pedido(self, pedido):
        """Remove marcador de pedido"""
        pid = pedido.id_pedido
        if pid in self.pedidos_desenhados:
            marker_id, text_id = self.pedidos_desenhados.pop(pid)
            self.delete(marker_id)
            self.delete(text_id)

    def desenhar_pedidos(self, pedidos_list):
        """Atualiza lista de pedidos no mapa"""
        existentes = set(self.pedidos_desenhados.keys())
        atuais = set(p.id_pedido for p in pedidos_list)

        # Remover pedidos que deixaram de existir
        for pid in existentes - atuais:
            marker_id, text_id = self.pedidos_desenhados.pop(pid)
            self.delete(marker_id)
            self.delete(text_id)

        # Desenhar pedidos atuais
        for p in pedidos_list:
            self.desenhar_pedido(p)

    def atualizar_veiculos(self, veiculos: dict):
        """Renderiza todos os veículos e suas rotas"""
        self.delete("veiculos")
        self.delete("rotas")

        for v in veiculos.values():
            x, y = self._pos(v.posicao)

            # Cor baseada no tipo
            color = "#0077cc" if v.tipo_veiculo() == "eletrico" else "#cc7700"

            # Desenhar quadrado do veículo
            self.create_rectangle(x - VEHICLE_HALF, y - VEHICLE_HALF,
                                 x + VEHICLE_HALF, y + VEHICLE_HALF,
                                 fill=color, outline="black",
                                 tags=("veiculos", f"veiculo_{v.id_veiculo}"))

            # Label do veículo
            self.create_text(x, y + 14, text=v.id_veiculo,
                           font=("Arial", 8), tags="veiculos")

            # Desenhar rota como linha tracejada
            if getattr(v, "rota", None) and len(v.rota) > 1:
                coords = [self._pos(node) for node in v.rota]
                for i in range(len(coords) - 1):
                    x1, y1 = coords[i]
                    x2, y2 = coords[i + 1]
                    self.create_line(x1, y1, x2, y2,
                                   fill=color, dash=(4, 3),
                                   width=2, tags="rotas")

    def atualizar(self, veiculos: dict, pedidos: list):
        """Atualiza renderização completa"""
        self.desenhar_grafo()  # Redesenhar grafo
        self.desenhar_pedidos(pedidos)  # Atualizar pedidos
        self.atualizar_veiculos(veiculos)  # Atualizar veículos
        self.desenhar_legenda()  # Garantir legenda visível
        self.update_idletasks()