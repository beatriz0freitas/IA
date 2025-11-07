 def constroi_grafo(self):
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

    # usar desenha("kk", False/True para mostrar tempos, escala à escolha)
    # o "kk" faz o grafico em escala com as distancias definidas
    def desenha(self, mode="coords", show_time=False, scale=1.0):
        """
        Args:
            mode: "coords" -> place nodes at (node.x, node.y) (visual edge length = geometric distance)
                "kk"     -> Kamada-Kawai layout using edge distance_km as target lengths
                "coords+kk" -> use node coords as initial positions, then run KK to match distance_km
            show_time: if True show travel_time_min labels; otherwise show distance_km
            scale: visual scale factor for coordinates or final layout
        """
        g = nx.Graph()

        # Add nodes with metadata
        for nid, node in self.nodes.items():
            g.add_node(nid, x=node.x, y=node.y, type=node.type)

        # Add edges and attach distance/time as attributes; avoid duplicating since graph is undirected
        for origin, edges in self.adj.items():
            for edge in edges:
                if g.has_edge(origin, edge.to_node):
                    continue
                g.add_edge(origin, edge.to_node,
                        distance=edge.distance_km,
                        time=edge.travel_time_min,
                        weight=edge.distance_km)  # weight used by KK

        # Choose layout
        pos = None
        if mode == "coords":
            # Use the node coordinates directly (scaled)
            pos = {nid: (data['x'] * scale, data['y'] * scale) for nid, data in g.nodes(data=True)}

        elif mode == "kk":
            # Kamada-Kawai trying to honor edge 'weight' as desired lengths
            # Lower weight -> closer nodes; KK uses 'weight' attribute by default if provided
            # We pass weight='weight' explicitly.
            pos = nx.kamada_kawai_layout(g, weight='weight', scale=scale)

        elif mode == "coords+kk":
            # Use coords as initial positions, then KK to better match distances.
            init_pos = {nid: (data['x'] * scale, data['y'] * scale) for nid, data in g.nodes(data=True)}
            # nx.kamada_kawai_layout accepts a 'pos' argument as initial guess
            pos = nx.kamada_kawai_layout(g, weight='weight', scale=scale, pos=init_pos)

        else:
            raise ValueError("mode must be one of: 'coords', 'kk', 'coords+kk'")

        # Draw nodes and labels
        nx.draw_networkx_nodes(g, pos, node_size=700, node_color='skyblue', edgecolors='black')
        nx.draw_networkx_labels(g, pos, font_weight='bold')

        # Draw edges
        nx.draw_networkx_edges(g, pos, width=2, alpha=0.8)

        # Edge labels: distance or time
        label_attr = 'time' if show_time else 'distance'
        labels = nx.get_edge_attributes(g, label_attr)
        # format labels
        edge_labels = {k: f"{v:.1f}" for k, v in labels.items()}
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_color='red')

        plt.axis('equal')
        plt.axis('off')
        plt.show()