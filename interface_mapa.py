import tkinter as tk
from modelo.grafo import Grafo, TipoNo

NODE_RADIUS = 10
VEHICLE_HALF = 6
SCALE = 90
OFFSET_X = 500  # Horizontal 
OFFSET_Y = 250  # Vertical 

class InterfaceMapa(tk.Canvas):
    def __init__(self, parent, grafo: Grafo, width=800, height=600):
        super().__init__(parent, bg="#f2fdf5", highlightthickness=0, width=width, height=height)
        self.grafo = grafo
        self.pack(expand=True, fill="both")
        self.veiculos_desenhados = {}   # id_veiculo -> canvas_id
        self.pedidos_desenhados = {}    # id_pedido -> (marker_id, text_id)
        self.pos_cache = {}             # id_no -> (x,y) pixels
        self.grafo_desenhado = False    # flag para evitar redesenho
        self.desenhar_grafo_estatico()
        self.draw_legend()

    def _pos(self, id_no):
        # cache das posições para evitar recalcular
        if id_no in self.pos_cache:
            return self.pos_cache[id_no]
        
        no = self.grafo.nos[id_no]
        x = no.posicaox * SCALE + OFFSET_X
        y = no.posicaoy * SCALE + OFFSET_Y
        self.pos_cache[id_no] = (x, y)
        return x, y

    def desenhar_grafo_estatico(self):
        if self.grafo_desenhado:
            return
        
        self.desenhar_arestas()
        self.desenhar_nos()
        self.grafo_desenhado = True

    def desenhar_arestas(self):
        self.delete("arestas")
        for origem, arestas in self.grafo.adjacentes.items():
            x1, y1 = self._pos(origem)
            for a in arestas:
                # evitar desenhar duas vezes a mesma aresta (grafo não direcionado)
                if origem < a.no_destino:
                    x2, y2 = self._pos(a.no_destino)
                    self.create_line(x1, y1, x2, y2, fill="#cfcfcf", width=2, tags="arestas")

    def desenhar_nos(self):
        self.delete("nos")
        for no in self.grafo.nos.values():
            x, y = self._pos(no.id_no)
            cor = {
                TipoNo.RECOLHA_PASSAGEIROS: "#6fd673",
                TipoNo.ESTACAO_RECARGA: "#77bfff",
                TipoNo.POSTO_ABASTECIMENTO: "#ffb366"
            }.get(no.tipo, "#95a5a6")

            self.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, 
                             x + NODE_RADIUS, y + NODE_RADIUS,
                             fill=cor, outline="#333", tags=("nos", f"no_{no.id_no}"))
            self.create_text(x, y - NODE_RADIUS - 10, 
                             text=no.id_no, font=("Arial", 9, "bold"), tags="nos")

    
    def draw_legend(self, x=10, y=200):
        self.delete("legenda")

        # layout da legenda — apresenta símbolo e texto
        linhas = [
            ("nos", "Zona de recolha", "#6fd673", "oval"),
            ("recarga", "Estação de recarga", "#77bfff", "oval"),
            ("posto", "Posto de abastecimento", "#ffb366", "oval"),
            ("eletrico", "Veículo Elétrico", "#0077cc", "rect"),
            ("combustao", "Veículo Combustão", "#cc7700", "rect"),
            ("pedido", "Pedido ativo", "#9b59b6", "pin"),
        ]

        spacing = 26
        for i, (label, color, shape) in enumerate(linhas):
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
        pid = pedido.id_pedido

        if pid in self.pedidos_desenhados:
            marker_id, text_id = self.pedidos_desenhados[pid]
            self.delete(marker_id)
            self.delete(text_id)
            del self.pedidos_desenhados[pid]

        x, y = self._pos(pedido.posicao_inicial)
        # marcador roxo para pedido
        marker = self.create_oval(x - 6, y - 6, x + 6, y + 6, 
                                 fill="#9b59b6", outline="#4a235a", 
                                 tags=("pedidos", f"pedido_{pid}"))
        label = self.create_text(x, y - 16, text=pid, 
                                font=("Arial", 8, "bold"), 
                                tags=("pedidos",))
        
        self.pedidos_desenhados[pid] = (marker, label)

    def remover_pedido(self, pedido):
        pid = pedido.id_pedido
        if pid in self.pedidos_desenhados:
            marker_id, text_id = self.pedidos_desenhados.pop(pid)
            self.delete(marker_id)
            self.delete(text_id)

    def desenhar_pedidos(self, pedidos_list):
        existentes = set(self.pedidos_desenhados.keys())
        atuais = set(p.id_pedido for p in pedidos_list)

        # Remove pedidos que já não existem
        for pid in existentes - atuais:
            marker_id, text_id = self.pedidos_desenhados.pop(pid)
            self.delete(marker_id)
            self.delete(text_id)

        # Desenha/atualiza pedidos atuais
        for p in pedidos_list:
            self.desenhar_pedido(p)


    def atualizar_veiculos(self, veiculos: dict):
        self.delete("veiculos")
        self.delete("rotas")

        for v in veiculos.values():
            x, y = self._pos(v.posicao)
            
            # Cor base por tipo
            if v.tipo_veiculo() == "eletrico":
                cor_base = "#0077cc"
            else:
                cor_base = "#cc7700"
            
            # Ajusta cor conforme estado
            if v.estado.value in ("recarregando", "reabastecendo"):
                cor = "#FFD700"  # Dourado quando a carregar
            elif v.estado.value == "a_servico":
                cor = "#00FF00"  # Verde quando com passageiros
            else:
                cor = cor_base
            
            # Desenha veículo
            self.create_rectangle(x - VEHICLE_HALF, y - VEHICLE_HALF, 
                                x + VEHICLE_HALF, y + VEHICLE_HALF,
                                fill=cor, outline="black", 
                                tags=("veiculos", f"veiculo_{v.id_veiculo}"))
            
            # Label com ID e autonomia
            label = f"{v.id_veiculo}\n{int(v.autonomia_km)}km"
            self.create_text(x, y + 16, text=label, 
                           font=("Arial", 7), tags="veiculos")

            # Desenha rota planeada
            if hasattr(v, "rota") and v.rota and len(v.rota) > 1:
                coords = [self._pos(node) for node in v.rota]
                for i in range(len(coords) - 1):
                    self.create_line(coords[i][0], coords[i][1], 
                                   coords[i+1][0], coords[i+1][1], 
                                   fill=cor_base, dash=(4, 3), width=2, 
                                   tags="rotas")

    def atualizar(self, veiculos: dict, pedidos: list):
        self.desenhar_pedidos(pedidos)
        self.atualizar_veiculos(veiculos)
        self.draw_legend()
        self.update_idletasks()
