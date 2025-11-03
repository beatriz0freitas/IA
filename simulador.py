

from grafo import Graph, Node, Edge
from veiculos import Vehicle, get_frota
from pedidos import Request
from collections import deque

# incorporar isto tudo numa classe que atue como uma especie de facade suponho
# TODO's
# -> fazer taxi passar do ponto de recolha para o destino (neste momento so chega ao primeiro)

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

    # dicionário de veiculos, tem um em K neste momento
    # algumas operações envolvem verificar linearmente pela frota se o taxi esta disponivel ou nao
    # guardar dois dicionarios, um para ocupado e outro para disponivel e mover de acordo com ocupação?
    frota = get_frota()
    
    # isto num ciclo de ticks que a cada tick tem uma chance de alterar condições
    # ou gerar requests

    request_queue = deque()
    req = Request(1, "A", "B", 2, 0, 'combustao')

    # colocar na queue ordenado por prioridades (TODO ordenado)
    request_queue.append(req)

    # assign first request in queue to best taxi
    curRequest = request_queue.pop()
    # (TODO) curTaxi = frota.get( curRequest.get_best_taxi(frota) ) returns id do melhor taxi para o pedido
    curTaxi = frota.get(1)

    # isto precisa de definir um path ate a recolha e depois ate ao destino
    # definir procuras com "checkpoint"? ou dois atributos path?
    curTaxi.set_path( g.bfs(curTaxi.position, curRequest.origin_position) )
    print(curTaxi.position)

    tickNum = 20
    for i in range(tickNum):
        for id in frota:
            taxi = frota[id]
            if taxi.path: # se está a tratar de um pedido
                print("Position: " + taxi.position)
                print(taxi.path)
                nextNodeId = taxi.get_next_path_node()
                taxi.move( g.get_edge(taxi.position, nextNodeId).distance_km, nextNodeId )


    # cada tick de tempo pode passar move a todos os taxis e, se nao tiverem path, nao mexem
    # se houver um update no ambiente, verificar reroutes melhores se tiver path e so depois move
    # check_reroutes(frota)



if __name__ == "__main__":
    main()