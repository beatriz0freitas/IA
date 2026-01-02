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
        self.rotas_pedidos = {}
        self.cores_pedidos = {}
        self.pos_cache = {}
        self.grafo_desenhado = False
        self.tooltip = None
        
        self.calcular_escala_e_offset()
        
        self.desenhar_grafo_estatico()
        self.draw_legend()
        
        # Eventos de hover
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Leave>", self.on_mouse_leave)

        self.vehicle_items = {}      # id_veiculo -> (shadow_id, rect_id, label_id)
        self.vehicle_pixel = {}      # id_veiculo -> (x, y) posição atual em pixels
        self.anim_job = {}           # id_veiculo -> after_id (para cancelar animações)
        self.dest_lines = {}   # id_veiculo -> line_id (linha até destino)



    def calcular_escala_e_offset(self):

        if not self.grafo.nos:
            self.offset_x = self.width // 2
            self.offset_y = self.height // 2
            self.scale = 50
            return
        
        xs = [no.posicaox for no in self.grafo.nos.values()]
        ys = [no.posicaoy for no in self.grafo.nos.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        largura_grafo = max_x - min_x
        altura_grafo = max_y - min_y
        
        margin = 0.075
        espaco_util_width = self.width * (1 - 2 * margin)
        espaco_util_height = self.height * (1 - 2 * margin)
        
        if largura_grafo > 0 and altura_grafo > 0:
            scale_x = espaco_util_width / largura_grafo
            scale_y = espaco_util_height / altura_grafo
            self.scale = min(scale_x, scale_y)
        else:
            self.scale = 50
        
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

    def desenhar_nos(self, estacoes_offline=None):
        self.delete("nos")
        if estacoes_offline is None:
            estacoes_offline = set()

        for no in self.grafo.nos.values():
            x, y = self._pos(no.id_no)

            # Verifica se está offline
            is_offline = no.id_no in estacoes_offline

            # Cores limpas e distintas
            if no.tipo == TipoNo.RECOLHA_PASSAGEIROS:
                cor = "#10b981"  # Verde esmeralda
                borda = "#059669"
            elif no.tipo == TipoNo.ESTACAO_RECARGA:
                if is_offline:
                    cor = "#64748b"  # Cinza (offline)
                    borda = "#475569"
                else:
                    cor = "#3b82f6"  # Azul vivo
                    borda = "#2563eb"
            elif no.tipo == TipoNo.POSTO_ABASTECIMENTO:
                if is_offline:
                    cor = "#64748b"  # Cinza (offline)
                    borda = "#475569"
                else:
                    cor = "#ef4444"  # Vermelho coral
                    borda = "#dc2626"
            else:
                cor = "#6b7280"
                borda = "#4b5563"

            # Nó principal
            self.create_oval(x - NODE_RADIUS, y - NODE_RADIUS,
                           x + NODE_RADIUS, y + NODE_RADIUS,
                           fill=cor, outline=borda, width=2,
                           tags=("nos", f"no_{no.id_no}"))

            # Marca X se offline
            if is_offline:
                self.create_line(x - 4, y - 4, x + 4, y + 4,
                               fill="#ffffff", width=2, tags="nos")
                self.create_line(x - 4, y + 4, x + 4, y - 4,
                               fill="#ffffff", width=2, tags="nos")

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

    def obter_cor_pedido(self, pedido_id):
        if pedido_id not in self.cores_pedidos:
            self.cores_pedidos[pedido_id] = self.paleta_cores[self.proximo_indice_cor % len(self.paleta_cores)]
            self.proximo_indice_cor += 1
        return self.cores_pedidos[pedido_id]
    
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

    def atualizar_veiculos(self, veiculos: dict, anim_ms: int = 450, frames: int = 18):
        # NÃO apagues "veiculos" nem "destinos" aqui — senão perdes animação.
        # Se quiseres apagar rotas antigas, apaga só as rotas (se ainda as desenhas):
        # self.delete("rotas")

        # Remove veículos que já não existem
        ids_atuais = set(v.id_veiculo for v in veiculos.values())
        ids_existentes = set(self.vehicle_items.keys())

        for vid in ids_existentes - ids_atuais:
            # remove linha destino
            line_id = self.dest_lines.pop(vid, None)
            if line_id:
                self.delete(line_id)

            # remove itens veículo
            shadow_id, rect_id, label_id = self.vehicle_items.pop(vid)
            self.delete(shadow_id)
            self.delete(rect_id)
            self.delete(label_id)

            self.vehicle_pixel.pop(vid, None)

            job = self.anim_job.pop(vid, None)
            if job:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass

        # Atualiza / cria veículos existentes
        for v in veiculos.values():
            vid = v.id_veiculo
            target_x, target_y = self._pos(v.posicao)

            # Cor por tipo/estado
            if v.tipo_veiculo() == "eletrico":
                cor = "#0ea5e9"
            else:
                cor = "#f59e0b"

            if v.estado.value in ("recarregando", "reabastecendo"):
                cor = "#fbbf24"
            elif v.estado.value == "a_servico":
                cor = "#10b981"

            # Se ainda não existe, cria no target (sem animação inicial)
            if vid not in self.vehicle_items:
                x, y = target_x, target_y

                # linha destino (se houver), criada já
                destino = v.rota[-1] if getattr(v, "rota", None) else None
                if destino and destino in self.grafo.nos and destino != v.posicao:
                    dx, dy = self._pos(destino)
                    line_id = self.create_line(
                        x, y, dx, dy,
                        fill="#fca5a5", width=1, dash=(3, 4),
                        tags=("destinos",)
                    )
                    self.dest_lines[vid] = line_id
                    self.tag_lower(line_id)

                shadow = self.create_rectangle(
                    x - VEHICLE_SIZE + 2, y - VEHICLE_SIZE + 2,
                    x + VEHICLE_SIZE + 2, y + VEHICLE_SIZE + 2,
                    fill="#d1d5db", outline=""
                )
                rect = self.create_rectangle(
                    x - VEHICLE_SIZE, y - VEHICLE_SIZE,
                    x + VEHICLE_SIZE, y + VEHICLE_SIZE,
                    fill=cor, outline="#ffffff", width=2
                )
                label = self.create_text(
                    x, y + VEHICLE_SIZE + 12, text=vid,
                    font=("Inter", 8, "bold"), fill="#374151"
                )

                self.vehicle_items[vid] = (shadow, rect, label)
                self.vehicle_pixel[vid] = (x, y)
                continue

            # Atualiza cor
            shadow_id, rect_id, label_id = self.vehicle_items[vid]
            self.itemconfig(rect_id, fill=cor)

            # Atualiza / remove a linha destino (sem apagar tudo)
            destino = v.rota[-1] if getattr(v, "rota", None) else None
            cur_x, cur_y = self.vehicle_pixel.get(vid, (target_x, target_y))

            if destino and destino in self.grafo.nos and destino != v.posicao:
                dx, dy = self._pos(destino)
                if vid not in self.dest_lines:
                    line_id = self.create_line(
                        cur_x, cur_y, dx, dy,
                        fill="#fca5a5", width=1, dash=(3, 4),
                        tags=("destinos",)
                    )
                    self.dest_lines[vid] = line_id
                else:
                    self.coords(self.dest_lines[vid], cur_x, cur_y, dx, dy)

                self.tag_lower(self.dest_lines[vid])
            else:
                line_id = self.dest_lines.pop(vid, None)
                if line_id:
                    self.delete(line_id)

            # Animar do pixel atual -> pixel alvo
            start_x, start_y = self.vehicle_pixel.get(vid, (target_x, target_y))

            # Se praticamente igual, só “snap”
            if abs(start_x - target_x) < 1 and abs(start_y - target_y) < 1:
                self._colocar_veiculo_em(vid, target_x, target_y)
                continue

            # Cancela animação anterior se existir
            job = self.anim_job.get(vid)
            if job:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass

            self._animar_veiculo(vid, start_x, start_y, target_x, target_y, anim_ms, frames)


    def _colocar_veiculo_em(self, vid: str, x: float, y: float):
        shadow_id, rect_id, label_id = self.vehicle_items[vid]

        self.coords(shadow_id,
                    x - VEHICLE_SIZE + 2, y - VEHICLE_SIZE + 2,
                    x + VEHICLE_SIZE + 2, y + VEHICLE_SIZE + 2)

        self.coords(rect_id,
                    x - VEHICLE_SIZE, y - VEHICLE_SIZE,
                    x + VEHICLE_SIZE, y + VEHICLE_SIZE)

        self.coords(label_id,
                    x, y + VEHICLE_SIZE + 12)

        self.vehicle_pixel[vid] = (x, y)

    def _animar_veiculo(self, vid: str, sx: float, sy: float, tx: float, ty: float,
                        anim_ms: int, frames: int):
        # Interpolação linear (chega bem para “visual cues”)
        step_ms = max(10, anim_ms // max(1, frames))
        dx = (tx - sx) / frames
        dy = (ty - sy) / frames

        def frame(i: int, x: float, y: float):
            if vid not in self.vehicle_items:
                return
            self._colocar_veiculo_em(vid, x, y)
            if i >= frames:
                self.anim_job.pop(vid, None)
                return
            self.anim_job[vid] = self.after(step_ms, lambda: frame(i + 1, x + dx, y + dy))

        frame(0, sx, sy)



    # Mostra tooltip apenas ao passar o rato sobre elemento
    def on_mouse_move(self, event):
        x, y = event.x, event.y
    
        self.delete("tooltip")
        self.tooltip = None

        # Verifica hover sobre rotas de pedidos
        for pedido_id, info_rota in self.rotas_pedidos.items():
            coords = info_rota['coords']
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                
                # Distância do ponto à linha
                if self.distancia_ponto_linha(x, y, x1, y1, x2, y2) < 8:
                    self.mostrar_tooltip_rota(x, y, pedido_id, info_rota)
                    return
        
        # Verifica veículos
        if hasattr(self, 'veiculos_ref'):
            for v in self.veiculos_ref.values():
                vx, vy = self._pos(v.posicao)
                if ((x - vx) ** 2 + (y - vy) ** 2) ** 0.5 <= VEHICLE_SIZE + 3:
                    self.mostrar_tooltip_veiculo(x, y, v)
                    return
        
        # Verifica nós
        for no_id, no in self.grafo.nos.items():
            nx, ny = self._pos(no_id)
            if ((x - nx) ** 2 + (y - ny) ** 2) ** 0.5 <= NODE_RADIUS + 2:
                self.mostrar_tooltip_no(x, y, no)
                return

    def distancia_ponto_linha(self, px, py, x1, y1, x2, y2):
        linha_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if linha_len_sq == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / linha_len_sq))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5


    def mostrar_tooltip_rota(self, x, y, pedido_id, info_rota):
        veiculo = info_rota['veiculo']
        cor = info_rota['cor']
        
        # Encontra o pedido
        pedido = None
        if hasattr(self, 'pedidos_ref'):
            for p in self.pedidos_ref:
                if p.id_pedido == pedido_id:
                    pedido = p
                    break
        
        width = 180
        height = 105
        
        tx = x + 15
        ty = y - height - 10
        
        self.create_rectangle(tx + 3, ty + 3, tx + width + 3, ty + height + 3,
                            fill="#e5e7eb", outline="", tags="tooltip")
        
        self.create_rectangle(tx, ty, tx + width, ty + height,
                            fill="#ffffff", outline=cor, width=3, tags="tooltip")
        
        self.create_rectangle(tx, ty, tx + width, ty + 25,
                            fill=cor, outline="", tags="tooltip")
        
        self.create_text(tx + width // 2, ty + 12,
                       text=f"Rota do Pedido {pedido_id}",
                       font=("Arial", 9, "bold"),
                       fill="#ffffff", tags="tooltip")
        
        # Informações
        if pedido:
            info_lines = [
                f"Veículo: {veiculo.id_veiculo}",
                f"Origem: {pedido.posicao_inicial.replace('_', ' ')}",
                f"Destino: {pedido.posicao_destino.replace('_', ' ')}",
                f"Passageiros: {pedido.passageiros} 👥",
            ]
        else:
            info_lines = [
                f"Veículo: {veiculo.id_veiculo}",
                f"Em deslocação...",
            ]
        
        for i, linha in enumerate(info_lines):
            self.create_text(tx + 10, ty + 40 + i * 16,
                           text=linha, anchor="w",
                           font=("Arial", 8),
                           fill="#374151", tags="tooltip")
        
        self.tag_raise("tooltip")

    def mostrar_tooltip_no(self, x, y, no):
        tipos_icon = {
            TipoNo.RECOLHA_PASSAGEIROS: ("Zona Recolha"),
            TipoNo.ESTACAO_RECARGA: ("Estação Recarga"),
            TipoNo.POSTO_ABASTECIMENTO: ("Posto Abastecimento")
        }

        tipo_nome = tipos_icon.get(no.tipo, ("Desconhecido"))
        nome_limpo = no.id_no.replace("_", " ")

        texto = f"{nome_limpo}"
        subtexto = tipo_nome

        padding = 10
        line_height = 18
        text_width = max(len(texto), len(subtexto)) * 7 + padding * 2

        tx = x + 15
        ty = y - 35

        self.create_rectangle(tx + 2, ty + 2,
                              tx + text_width + 2, ty + line_height * 2 + padding + 2,
                              fill="#e5e7eb", outline="", tags="tooltip")

        self.create_rectangle(tx, ty,
                              tx + text_width, ty + line_height * 2 + padding,
                              fill="#ffffff", outline="#d1d5db", width=2, tags="tooltip")

        self.create_text(tx + text_width // 2, ty + 10,
                         text=texto, font=("Arial", 9, "bold"), 
                         fill="#111827", tags="tooltip")

        self.create_text( tx + text_width // 2, ty + 26,
                          text=subtexto, font=("Arial", 8),
                          fill="#6b7280", tags="tooltip")

        self.tag_raise("tooltip")


    def mostrar_tooltip_veiculo(self, x, y, veiculo):
        tipo = "Elétrico" if veiculo.tipo_veiculo() == "eletrico" else "Combustão"
        autonomia_pct = int((veiculo.autonomia_km / veiculo.autonomiaMax_km) * 100)

        if autonomia_pct > 60:
            cor_bateria = "#10b981"  # Verde
        elif autonomia_pct > 30:
            cor_bateria = "#f59e0b"  # Laranja
        else:
            cor_bateria = "#ef4444"  # Vermelho

        # Estados em português
        estados_pt = {
            "disponivel": "Disponível",
            "a_servico": "Com Passageiros",
            "recarregando": "A reccarregar",
            "reabastecendo": "A reabastecer",
            "deslocando": "Em Movimento",
            "indisponivel": "Indisponível"
        }
        estado_texto = estados_pt.get(veiculo.estado.value, veiculo.estado.value)

        width = 160
        height = 95
        padding = 12

        tx = x + 15
        ty = y - height - 10

        self.create_rectangle(
            tx + 3, ty + 3,
            tx + width + 3, ty + height + 3,
            fill="#e5e7eb", outline="",
            tags="tooltip"
        )

        self.create_rectangle(
            tx, ty,
            tx + width, ty + height,
            fill="#ffffff", outline="#d1d5db", width=2,
            tags="tooltip"
        )

        self.create_text(
            tx + width // 2, ty + 15,
            text=f"{veiculo.id_veiculo}",
            font=("Arial", 10, "bold"),
            fill="#111827",
            tags="tooltip"
        )

        self.create_text(
            tx + width // 2, ty + 35,
            text=tipo,
            font=("Arial", 9),
            fill="#4b5563",
            tags="tooltip"
        )

        # Barra de autonomia (fundo)
        barra_x = tx + padding
        barra_y = ty + 50
        barra_width = width - padding * 2
        barra_height = 8

        self.create_rectangle(
            barra_x, barra_y,
            barra_x + barra_width, barra_y + barra_height,
            fill="#e5e7eb", outline="",
            tags="tooltip"
        )

        preenchimento = int((barra_width * autonomia_pct) / 100)
        self.create_rectangle(
            barra_x, barra_y,
            barra_x + preenchimento, barra_y + barra_height,
            fill=cor_bateria, outline="",
            tags="tooltip"
        )

        self.create_text(
            tx + width // 2, barra_y + barra_height // 2,
            text=f"{autonomia_pct}%",
            font=("Arial", 7, "bold"),
            fill="#ffffff",
            tags="tooltip"
        )

        self.create_text(
            tx + width // 2, ty + 75,
            text=estado_texto,
            font=("Arial", 8),
            fill="#6b7280",
            tags="tooltip"
        )

        self.tag_raise("tooltip")

    # Remove tooltip
    def on_mouse_leave(self, event):
        if self.tooltip:
            self.delete("tooltip")
            self.tooltip = None

    def atualizar(self, veiculos: dict, pedidos: list):
        self.delete("tooltip")

        self.pedidos_ref = pedidos
        self.veiculos_ref = veiculos
        
        self.desenhar_pedidos(pedidos)
        self.atualizar_veiculos(veiculos)
        self.draw_legend()
        self.update_idletasks()