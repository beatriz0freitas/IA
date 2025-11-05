
from dataclasses import dataclass, field
import heapq
from grafo import Graph, Node, Edge
from veiculos import Vehicle, get_frota
from pedidos import Request
from uteis import euclidean_distance
from math import inf as infinito


# incorporar isto tudo numa classe que atue como uma especie de facade suponho
# TODO's
# -> fazer taxi passar do ponto de recolha para o destino (neste momento so chega ao primeiro)
# -> limpar tudo isto
# -> meter estrutura para requests, e preciso para metricas
# -> guardar requests todos numa estrutura, precisas para métricas depois
# -> ter em conta reabastecimentos

# classe organizadora da frota(?), mais fácil que usar apenas uma lista suponho...?
# usava mais memoria mas escusava percorrer a frota inteira
# TODO (noutro modulo claro)
@dataclass
class Frota:
    frotaOcupada: list
    frotaLivre: list
    frotaCombustao: list

@dataclass
class Simulation:
    # tempo (em minutos? abstrato tipo ticks?)
    time: int = 0
    # dicionário de táxis, podia ser classe a parte que organiza por categoria (como disponiveis) para procura mais rapida
    frota = get_frota() # delegar operações nisto para uma classe à parte(?)
    # mapa de teste
    grafo = Graph().constroi_grafo()
    # heap de requests que deve ser ordenada por prioridade (heapify em add_request)
    # garante menor valor a frente, mas nao é ordenada...
    request_queue = list()

    # lista de pedidos (para métricas)
    # indexes ordenados cronologicamente, evita ser dicionario
    request_registry = list()

    # pode-se passar o grafo como argumento até
    def run_Simulation(self):
        # self.grafo.desenha(mode="kk", show_time=False, scale=2.0)

        # TODO definir lista para testes, scheduled e depois maybe pedidos aleatorios
        self.addRequest(1, "A", "B", 2, 0, 'combustao', 0)

        # TODO
        cancel = ""
        while cancel == "":
            print("Tick: " + str(self.time))
            if self.request_queue:
                current_request = self.get_next_request()
                self.handle_request(current_request)

            for id, taxi in self.frota.items():
                print("Position: " + taxi.position)
                if taxi.path:
                    print("Path: " + str(taxi.path))
                    # acoplar numa função move_taxi ig?
                    # nextNodeId = taxi.get_next_path_node()
                    # taxi.move( self.grafo.get_edge(taxi.position, nextNodeId).distance_km, nextNodeId )
                    self.move_taxi(taxi)
    
            self.time += 1
            print("Press Enter to continue the simulation. Any Key to stop.")
            cancel = input()

    
    # requests precisam de id sequer...?
    def addRequest(self, id: int, 
                   origin: str, destination: str, 
                   passengers: int, schedule_request: int,
                   environmental, priority: int):
        req = Request(id, origin, destination, passengers, schedule_request, environmental, priority, "")
        self.request_queue.append(req)
        heapq.heapify(self.request_queue)
        self.request_registry.append(req)

    def get_next_request(self):
        return heapq.heappop(self.request_queue)
    
    # TODO como deve ser
    #       (isto nao pertence aqui pois nao...?)
    #      -> antes passar frota como argumento e passar o método para request? mas preciso das infos do nodo para distancias
    # retorna id do melhor taxi para o pedido (por agora o mais próximo do pickup)
    def get_best_taxi(self, request):
        bestTaxi_id = None
        bestDistance = infinito
        for id, taxi in self.frota.items():
            distance = euclidean_distance(self.grafo.nodes.get(taxi.position),
                                          self.grafo.nodes.get(request.origin_position))
            if taxi.available and distance < bestDistance:
                bestTaxi_id = id
                bestDistance = distance

        return bestTaxi_id
    
    # descobre a melhor rota para um dado request
    # TODO isto fode nos reroutes se ele ja tiver chegado à recolha, tem de se diferenciar isso
    #       ou com dois atributos path que diferenciem ou um bool qualquer
    def get_route_for_request(self, request: Request):
        taxi = self.frota.get(request.assigned_taxi_id)
        return self.grafo.bfs_com_checkpoint(taxi.position, request.origin_position, request.destination_position)

    def set_taxi_route(self, taxi_id, route):
        taxi = self.frota.get(taxi_id)
        taxi.set_path(route)

    # usa as funções acima para iniciar o request, dando setup a um taxi com rota
    def handle_request(self, request: Request):
        taxi_id = self.get_best_taxi(request)
        request.assign_taxi(taxi_id)
        route = self.get_route_for_request(request)
        self.set_taxi_route(taxi_id, route)

    def move_taxi(self, taxi):
        nextNodeId = taxi.get_next_path_node()
        taxi.move( self.grafo.get_edge(taxi.position, nextNodeId).distance_km, nextNodeId )

def main():
    simulador = Simulation()
    simulador.run_Simulation()

    # cada tick de tempo pode passar move a todos os taxis e, se nao tiverem path, nao mexem
    # se houver um update no ambiente, verificar reroutes melhores se tiver path e so depois move
    # check_reroutes(frota)


if __name__ == "__main__":
    main()