

from grafo import Graph, Node, Edge
from veiculos import Vehicle
from pedidos import Request


# até podemos passar como argumentos mapas de teste diferentes ig
def constroi_grafo():
    g = Graph()

    coords = {
        "A": (0, 1),   
        "B": (1, 2),  
        "C": (1, 0),    
        "D": (2, 1),   
        "E": (3, 2),   
        "F": (3, 0), 
        "G": (4, 1),
        "H": (5, 2),
        "I": (5, 0),
        "J": (6, 1),

        "K": (4, 3),
        "L": (2, 3)
    }

    # Adicionar nodos, por agora todas as zonas são iguais
    for nid, (x, y) in coords.items():
        g.add_node(Node(id=nid, x=x, y=y, type="zona"))

    # (src, dest, distance, min_time)
    g.add_edge("A", "B", 1.0, 2.5)
    g.add_edge("A", "C", 1.2, 3.0)
    g.add_edge("A", "D", 2.0, 4.2)
    g.add_edge("B", "D", 1.5, 3.5)
    g.add_edge("B", "E", 2.0, 4.4)
    g.add_edge("C", "D", 1.8, 4.0)
    g.add_edge("C", "F", 2.2, 4.8)
    g.add_edge("D", "E", 1.3, 3.0)
    g.add_edge("D", "F", 1.6, 3.6)
    g.add_edge("D", "G", 2.0, 4.3)
    g.add_edge("E", "H", 2.2, 5.0)
    g.add_edge("E", "G", 1.5, 3.3)
    g.add_edge("F", "G", 1.4, 3.2)
    g.add_edge("F", "I", 2.3, 5.0)
    g.add_edge("G", "H", 1.8, 4.1)
    g.add_edge("G", "I", 2.0, 4.4)
    g.add_edge("G", "J", 2.5, 5.5)
    g.add_edge("H", "J", 2.0, 4.2)
    g.add_edge("I", "J", 2.2, 4.8)

    g.add_edge("H", "K", 1.5, 3.3)
    g.add_edge("B", "L", 1.8, 3.8)
    g.add_edge("E", "L", 1.6, 3.5)

    return g


def main():
    g = constroi_grafo()
    g.desenha(mode="kk", show_time=False, scale=2.0)



if __name__ == "__main__":
    main()