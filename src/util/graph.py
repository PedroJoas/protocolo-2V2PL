import networkx as nx

class Graph:

    def __init__(self, graph) -> None:
        self.graph = graph
    

    def add_nodes(self, schedule_parsed):
        """  
        Função recebe o schedule já tratado e adiciona as vértices no grafo

        Entrada:
        schedule_parsed: Type dict
        """

        for processo in schedule_parsed:
            self.graph.add_node(f'T{processo[1]}')

       
    def detect_deadlocks(self):
        try:
            cycle = nx.find_cycle(self.graph, orientation='original')
            print("Ciclo encontrado:", cycle)
        except nx.NetworkXNoCycle:
            print("Nenhum ciclo encontrado.")




    def add_edges(self, waits):
        """  
        Função recebe os waits e adiciona as arestas no grafo

        Entrada:
        waits: Type dict
        """

        for wait in waits.items():
            edge = [(wait[0], t) for t in wait[1]]
        
            self.graph.add_edges_from(edge)
        