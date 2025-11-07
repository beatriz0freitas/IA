import tkinter as tk
from modelo.grafo import Grafo, No, TipoNo

class InterfaceMapa(tk.Canvas):
    def __init__(self, parent, grafo: Grafo):
        super().__init__(parent, bg="#f2fdf5", highlightthickness=0)
        self.grafo = grafo
        self.escala = 70  # controla o espaçamento visual
        self.veiculos_desenhados = {}

        self.desenhar_grafo()

    def desenhar_grafo(self):
        for origem, arestas in self.grafo.adjacentes.items():
            x1, y1 = self._pos(origem)
            for aresta in arestas:
                x2, y2 = self._pos(aresta.no_destino)
                self.create_line(x1, y1, x2, y2, 
                                 fill="#a0a0a0", 
                                 width=2)

        for no in self.grafo.nos.values():
            x, y = self._pos(no.id_no)
            cor = {
                TipoNo.RECOLHA_PASSAGEIROS: "#6fd673",
                TipoNo.ESTACAO_RECARGA: "#77bfff",
                TipoNo.POSTO_ABASTECIMENTO: "#ffb366"
            }[no.tipo]
            self.create_oval(x - 10, 
                             y - 10, 
                             x + 10, 
                             y + 10, 
                             fill=cor, 
                             outline="black")
            self.create_text(x, 
                             y - 18, 
                             text=no.id_no, 
                             font=("Arial", 10, "bold"))

    def _pos(self, id_no):
        no = self.grafo.nos[id_no]
        return no.posicaox * self.escala + 50, no.posicaoy * self.escala + 50

    # Atualiza visualmente a posição dos veículos
    def atualizar_veiculos(self, veiculos):
        for idv, v in veiculos.items():
            x, y = self._pos(v.posicao)
            if idv in self.veiculos_desenhados:
                self.coords(self.veiculos_desenhados[idv], 
                            x - 6, 
                            y - 6, 
                            x + 6, 
                            y + 6)
            else:
                cor = "#0077cc" if v.tipo_veiculo() == "eletrico" else "#cc7700"
                self.veiculos_desenhados[idv] = self.create_rectangle(x - 6, 
                                                                      y - 6, 
                                                                      x + 6, 
                                                                      y + 6, 
                                                                      fill=cor, 
                                                                      outline="black"
)
