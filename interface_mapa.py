import tkinter as tk
from modelo.grafo import Grafo, TipoNo

NODE_RADIUS = 10
VEHICLE_SIZE = 8
SCALE = 40 

class InterfaceMapa(tk.Canvas):
    def __init__(self, parent, grafo: Grafo, width=900, height=700):
        super().__init__(parent, bg="#ffffff", highlightthickness=0, width=width, height=height)
        self.grafo = grafo
        self.width = width
        self.height = height
        self.pack(expand=True, fill="both")
        
        self.veiculos_desenhados = {}
        self.pedidos_desenhados = {}
        self.pos_cache = {}
        self.grafo_desenhado = False
        self.tooltip = None
        
        self.calcular_escala_e_offset()
        
        self.desenhar_grafo_estatico()
        self.draw_legend()
        
        # Eventos de hover
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Leave>", self.on_mouse_leave)

    def calcular_escala_e_offset(self):
        if not self.grafo.nos:
            self.offset_x = self.width // 2
            self.offset_y = self.height // 2
            self.scale = 40
            return
        
        # Encontra limites do grafo
        xs = [no.posicaox for no in self.grafo.nos.values()]
        ys = [no.posicaoy for no in self.grafo.nos.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        largura_grafo = max_x - min_x
        altura_grafo = max_y - min_y
        
        # Margens (15% de cada lado)
        margin = 0.15
        espaco_util_width = self.width * (1 - 2 * margin)
        espaco_util_height = self.height * (1 - 2 * margin)
        
        # Calcula escala que melhor se ajusta
        if largura_grafo > 0 and altura_grafo > 0:
            scale_x = espaco_util_width / largura_grafo
            scale_y = espaco_util_height / altura_grafo
            self.scale = min(scale_x, scale_y)
        else:
            self.scale = 40
        
        # Calcula offset para centralizar
        centro_grafo_x = (min_x + max_x) / 2
        centro_grafo_y = (min_y + max_y) / 2
        
        self.offset_x = self.width // 2 - (centro_grafo_x * self.scale)
        self.offset_y = self.height // 2 - (centro_grafo_y * self.scale)

    # Converte coordenadas do grafo para pixels"""
    def _pos(self, id_no):
        if id_no in self.pos_cache:
            return self.pos_cache[id_no]
        
        no = self.grafo.nos[id_no]
        x = no.posicaox * self.scale + self.offset_x
        y = no.posicaoy * self.scale + self.offset_y
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
                if origem < a.no_destino:
                    x2, y2 = self._pos(a.no_destino)
                    self.create_line(x1, y1, x2, y2, 
                                    fill="#d1d5db", width=2, 
                                    tags="arestas")

    def desenhar_nos(self):
        self.delete("nos")
        for no in self.grafo.nos.values():
            x, y = self._pos(no.id_no)
            
            # Cores limpas e distintas
            if no.tipo == TipoNo.RECOLHA_PASSAGEIROS:
                cor = "#10b981"  # Verde esmeralda
                borda = "#059669"
            elif no.tipo == TipoNo.ESTACAO_RECARGA:
                cor = "#3b82f6"  # Azul vivo
                borda = "#2563eb"
            elif no.tipo == TipoNo.POSTO_ABASTECIMENTO:
                cor = "#ef4444"  # Vermelho coral
                borda = "#dc2626"
            else:
                cor = "#6b7280"
                borda = "#4b5563"
            
            # Sombra sutil
            self.create_oval(x - NODE_RADIUS + 1, y - NODE_RADIUS + 1, 
                           x + NODE_RADIUS + 1, y + NODE_RADIUS + 1,
                           fill="#d1d5db", outline="", 
                           tags="nos_sombra")
            
            # Nó principal
            self.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, 
                           x + NODE_RADIUS, y + NODE_RADIUS,
                           fill=cor, outline=borda, width=2,
                           tags=("nos", f"no_{no.id_no}"))
            
            # Label
            self.create_text(x, y - NODE_RADIUS - 12, 
                           text=no.id_no.replace("_", " "), 
                           font=("Arial", 7, "bold"), 
                           fill="#374151",
                           tags="nos_label")

    def draw_legend(self):
        self.delete("legenda")
        
        x, y = 20, 20
        self.create_rectangle(x - 10, y - 10, x + 200, y + 155, 
                            fill="#ffffff", outline="#e5e7eb", width=2,
                            tags="legenda")
        
        self.create_text(x + 95, y + 5, 
                       text="Legenda", 
                       font=("Inter", 11, "bold"), 
                       fill="#111827",
                       tags="legenda")
        
        self.create_line(x, y + 20, x + 190, y + 20,
                        fill="#e5e7eb", width=1, tags="legenda")
        
        items = [
            ("Zona de recolha", "#10b981", "circle"),
            ("Estação recarga", "#3b82f6", "circle"),
            ("Posto abastecimento", "#ef4444", "circle"),
            ("Veículo Elétrico", "#0ea5e9", "square"),
            ("Veículo Combustão", "#f59e0b", "square"),
            ("Pedido ativo", "#8b5cf6", "diamond"),
        ]
        
        spacing = 20
        for i, (label, color, shape) in enumerate(items):
            yy = y + 35 + i * spacing
            
            if shape == "circle":
                self.create_oval(x + 5, yy - 6, x + 17, yy + 6, 
                               fill=color, outline="", tags="legenda")
            elif shape == "square":
                self.create_rectangle(x + 5, yy - 6, x + 17, yy + 6, 
                                    fill=color, outline="", tags="legenda")
            elif shape == "diamond":
                self.create_polygon(x + 11, yy - 7, x + 18, yy, x + 11, yy + 7, x + 4, yy,
                                  fill=color, outline="", tags="legenda")
            
            self.create_text(x + 28, yy, 
                           text=label, anchor="w", 
                           font=("Inter", 9), 
                           fill="#4b5563",
                           tags="legenda")

    def desenhar_pedido(self, pedido):
        pid = pedido.id_pedido

        if pid in self.pedidos_desenhados:
            self.delete(f"pedido_{pid}")
        
        x, y = self._pos(pedido.posicao_inicial)
        
        # Halo pulsante
        self.create_oval(x - 12, y - 12, x + 12, y + 12, 
                        fill="", outline="#c4b5fd", width=2,
                        tags=("pedidos", f"pedido_{pid}"))
        
        # Diamante
        marker = self.create_polygon(
            x, y - 8,      # Topo
            x + 8, y,      # Direita
            x, y + 8,      # Baixo
            x - 8, y,      # Esquerda
            fill="#8b5cf6", outline="#7c3aed", width=2,
            tags=("pedidos", f"pedido_{pid}")
        )
        
        label = self.create_text(x, y - 20, text=pid, 
                                font=("Inter", 8, "bold"), 
                                fill="#6d28d9",
                                tags=("pedidos", f"pedido_{pid}"))
        
        self.pedidos_desenhados[pid] = (marker, label)

    def remover_pedido(self, pedido):
        pid = pedido.id_pedido
        if pid in self.pedidos_desenhados:
            self.pedidos_desenhados.pop(pid)
        self.delete(f"pedido_{pid}")

    def desenhar_pedidos(self, pedidos_list):
        existentes = set(self.pedidos_desenhados.keys())
        atuais = set(p.id_pedido for p in pedidos_list)
        
        for pid in existentes - atuais:
            self.remover_pedido(type('obj', (object,), {'id_pedido': pid})())

        for p in pedidos_list:
            self.desenhar_pedido(p)

    def atualizar_veiculos(self, veiculos: dict):
        self.delete("veiculos")
        self.delete("rotas")

        for v in veiculos.values():
            x, y = self._pos(v.posicao)
            
            # Cores por tipo
            if v.tipo_veiculo() == "eletrico":
                cor = "#0ea5e9"  # Azul cyan
            else:
                cor = "#f59e0b"  # Laranja
            
            # Cor por estado
            if v.estado.value in ("recarregando", "reabastecendo"):
                cor = "#fbbf24"  # Amarelo
            elif v.estado.value == "a_servico":
                cor = "#10b981"  # Verde
            
            # Desenha rota (atrás)
            if hasattr(v, "rota") and v.rota and len(v.rota) > 1:
                coords = [self._pos(node) for node in v.rota]
                
                # Linha tracejada colorida
                for i in range(len(coords) - 1):
                    self.create_line(coords[i][0], coords[i][1], 
                                   coords[i+1][0], coords[i+1][1], 
                                   fill=cor, dash=(8, 4), width=3, 
                                   tags="rotas")
            
            # Sombra
            self.create_rectangle(x - VEHICLE_SIZE + 2, y - VEHICLE_SIZE + 2, 
                                x + VEHICLE_SIZE + 2, y + VEHICLE_SIZE + 2,
                                fill="#d1d5db", outline="",
                                tags="veiculos")
            
            # Veículo
            self.create_rectangle(x - VEHICLE_SIZE, y - VEHICLE_SIZE, 
                                x + VEHICLE_SIZE, y + VEHICLE_SIZE,
                                fill=cor, outline="#ffffff", width=2,
                                tags=("veiculos", f"veiculo_{v.id_veiculo}"))
            
            # Label
            self.create_text(x, y + VEHICLE_SIZE + 12, text=v.id_veiculo, 
                           font=("Inter", 8, "bold"), 
                           fill="#374151",
                           tags="veiculos")

    # Mostra tooltip ao passar o mouse"""
    def on_mouse_move(self, event):
        x, y = event.x, event.y
        
        if self.tooltip:
            self.delete(self.tooltip)
            self.tooltip = None
        
        # Verifica nós
        for no_id, no in self.grafo.nos.items():
            nx, ny = self._pos(no_id)
            if ((x - nx) ** 2 + (y - ny) ** 2) ** 0.5 < NODE_RADIUS + 5:
                self.mostrar_tooltip_no(x, y, no)
                return
        
        # Verifica veículos
        if hasattr(self, 'veiculos_ref'):
            for v in self.veiculos_ref.values():
                vx, vy = self._pos(v.posicao)
                if abs(x - vx) < 20 and abs(y - vy) < 20:
                    self.mostrar_tooltip_veiculo(x, y, v)
                    return

    def mostrar_tooltip_no(self, x, y, no):
        tipos = {
            TipoNo.RECOLHA_PASSAGEIROS: "Zona Recolha",
            TipoNo.ESTACAO_RECARGA: "Estação Recarga",
            TipoNo.POSTO_ABASTECIMENTO: "Posto Abastecimento"
        }
        
        texto = f"{no.id_no} • {tipos.get(no.tipo, '?')}"
        
        self.tooltip = self.create_rectangle(x + 15, y - 15, x + 180, y + 10,
                                            fill="#1f2937", outline="#374151", width=1,
                                            tags="tooltip")
        
        self.create_text(x + 97, y - 3, text=texto, 
                       font=("Inter", 9), fill="#ffffff",
                       tags="tooltip")


    def mostrar_tooltip_veiculo(self, x, y, veiculo):
        tipo = "Elétrico" if veiculo.tipo_veiculo() == "eletrico" else "Combustão"
        autonomia_pct = int((veiculo.autonomia_km / veiculo.autonomiaMax_km) * 100)
        
        texto = f"{veiculo.id_veiculo} • {tipo} • {autonomia_pct}%"
        
        self.tooltip = self.create_rectangle(x + 15, y - 15, x + 200, y + 10,
                                            fill="#1f2937", outline="#374151", width=1,
                                            tags="tooltip")
        
        self.create_text(x + 107, y - 3, text=texto, 
                       font=("Inter", 9), fill="#ffffff",
                       tags="tooltip")

    # Remove tooltip
    def on_mouse_leave(self, event):
        if self.tooltip:
            self.delete(self.tooltip)
            self.tooltip = None

    def atualizar(self, veiculos: dict, pedidos: list):
        self.veiculos_ref = veiculos
        self.desenhar_pedidos(pedidos)
        self.atualizar_veiculos(veiculos)
        self.draw_legend()
        self.update_idletasks()