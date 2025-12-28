from modelo.pedidos import Pedido, EstadoPedido
from gestao.simulador import Simulador

"""
Gera 30 pedidos para 60 minutos de simulação (frota pequena: 4 veículos).
- Mistura centro/periferia com hotspots (Centro/Praça/Shopping/Estação_Metro).
- Inclui preferências ambientais (eletrico/combustao/qualquer) de forma compatível
  com 2 elétricos + 2 combustão (sem tornar impossível).
- Instantes distribuídos ao longo dos 60 minutos com alguns mini-picos.
"""
class PedidosDemo:

    @staticmethod
    def criar_pedidos_demo(simulador: Simulador):
        pedidos = [
            Pedido("P1",  "Shopping",               "Hospital",              2,  2, 2, "eletrico",  EstadoPedido.PENDENTE, None, None, 15),
            Pedido("P2",  "Centro",                 "Aeroporto",             1,  4, 3, "qualquer",  EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P3",  "Universidade",           "Praça",                 3,  6, 1, "combustao", EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P4",  "Bairro_Norte1",          "Estação_Metro",         1,  8, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P5",  "Parque_Tec",             "Centro",                1, 10, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 22),

            # mini-pico (12-16)
            Pedido("P6",  "Centro_Comercial_Oeste", "Shopping",              1, 12, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 12),
            Pedido("P7",  "Praça",                  "Recarga_Norte",          1, 13, 2, "eletrico",  EstadoPedido.PENDENTE, None, None, 12),
            Pedido("P8",  "Bairro_Este",            "Hospital",              2, 14, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P9",  "Shopping",               "Universidade",          2, 15, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 15),
            Pedido("P10", "Estação_Metro",          "Centro",                1, 16, 3, "qualquer",  EstadoPedido.PENDENTE, None, None, 10),

            # fase média (18-28)
            Pedido("P11", "Industrial",             "Recarga_Sul",            1, 18, 2, "eletrico",  EstadoPedido.PENDENTE, None, None, 12),
            Pedido("P12", "Bairro_Sul",             "Centro",                2, 19, 1, "combustao", EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P13", "Bairro_Norte2",          "Praça",                 1, 21, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P14", "Suburbio_Oeste1",        "Centro",                1, 23, 2, "combustao", EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P15", "Aeroporto",              "Centro",                2, 25, 3, "qualquer",  EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P16", "Porto",                  "Estadio",               2, 26, 3, "eletrico",  EstadoPedido.PENDENTE, None, None, 25),
            Pedido("P17", "Praia",                  "Bairro_Este",            1, 27, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 25),
            Pedido("P18", "Escola_Norte",           "Bairro_Norte1",         1, 28, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 15),

            # mini-pico (30-36)
            Pedido("P19", "Centro",                 "Centro_Comercial_Oeste", 1, 30, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 12),
            Pedido("P20", "Hospital",               "Recarga_Centro",          1, 31, 2, "eletrico",  EstadoPedido.PENDENTE, None, None, 10),
            Pedido("P21", "Universidade",           "Bairro_Norte2",          2, 32, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P22", "Parque_Tec",             "Aeroporto",              1, 33, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 12),
            Pedido("P23", "Suburbio_Oeste2",        "Parque_Tec",             1, 35, 2, "eletrico",  EstadoPedido.PENDENTE, None, None, 22),
            Pedido("P24", "Bairro_Sul",             "Praia",                  3, 36, 2, "combustao", EstadoPedido.PENDENTE, None, None, 30),

            # fase final (40-58): transversais/longas
            Pedido("P25", "Bairro_Norte1",          "Industrial",             1, 40, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 25),
            Pedido("P26", "Estadio",                "Praça",                  2, 42, 2, "qualquer",  EstadoPedido.PENDENTE, None, None, 18),
            Pedido("P27", "Bairro_Este",            "Centro",                1, 44, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 20),
            Pedido("P28", "Aeroporto",              "Bairro_Norte2",          1, 46, 2, "combustao", EstadoPedido.PENDENTE, None, None, 25),
            Pedido("P29", "Centro_Comercial_Oeste", "Porto",                  2, 47, 3, "combustao", EstadoPedido.PENDENTE, None, None, 30),
            Pedido("P30", "Recarga_Praia",          "Posto_Sul",              1, 48, 1, "qualquer",  EstadoPedido.PENDENTE, None, None, 15),
        ]


        for p in pedidos:
            simulador.agendar_pedido(p)

        return simulador
