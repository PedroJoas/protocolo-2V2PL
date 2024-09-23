import networkx as nx

class Graph:

    def __init__(self, schedule_parsed) -> None:
        self.graph = nx.DiGraph()
        self._add_nodes(schedule_parsed)
    

    def _add_nodes(self, schedule_parsed: dict):
        """
        Adiciona vértices ao grafo com base nas transações do schedule.

        Esta função recebe um dicionário contendo o schedule já processado e 
        adiciona vértices ao grafo, onde cada vértice representa uma transação.

        Args:
            schedule_parsed (dict): Um dicionário contendo as transações e suas operações.
                                    O formato esperado é:
                                    {transacao_id: [(operacao, objeto)]}, onde:
                                    - `transacao_id` (int): Identificador da transação.
                                    - `operacao` (str): Operação realizada pela transação 
                                    ('r' para leitura, 'w' para escrita).
                                    - `objeto` (str): O objeto acessado na operação.

        Example:
            schedule_parsed = {1: [('r', 'x')], 2: [('w', 'y')]}
            Para esse `schedule_parsed`, os vértices 'T1' e 'T2' serão adicionados ao grafo.

        """

        for operacao in schedule_parsed:
            self.graph.add_node(f'T{operacao[0]}')

       
    def detect_deadlocks(self):
        """
        Detecta deadlocks no grafo de espera de transações.

        Esta função verifica se há ciclos no grafo que representam dependências 
        circulares entre transações. A presença de um ciclo indica a existência 
        de um deadlock. Se um ciclo for encontrado, ele é impresso; caso contrário, 
        a função indica que não há ciclos.

        Utiliza a função `nx.find_cycle` da biblioteca NetworkX para identificar ciclos 
        orientados no grafo de transações.

        Raises:
            NetworkXNoCycle: Exceção gerada automaticamente se nenhum ciclo for encontrado.

        Example:
            Ciclo encontrado: [('T1', 'T2'), ('T2', 'T3'), ('T3', 'T1')]
            Nenhum ciclo encontrado.
        """

        try:
            cycle = nx.find_cycle(self.graph, orientation='original')
            print("Ciclo encontrado:", cycle)
        except nx.NetworkXNoCycle:
            print("Nenhum ciclo encontrado.")




    def add_edges(self, waits: dict):
        """
        Adiciona arestas ao grafo de espera de transações com base no dicionário de dependências (`waits`).

        Esta função recebe o dicionário `waits`, que mapeia transações para outras transações das quais elas dependem. 
        A função então adiciona as arestas correspondentes ao grafo, onde cada aresta representa uma dependência 
        (bloqueio) de uma transação em relação a outra.

        Args:
            waits (dict): Um dicionário onde:
                        - A chave é a transação bloqueada.
                        - O valor é uma lista de tuplas, onde cada tupla contém a transação bloqueante e o objeto 
                            que causou o bloqueio.
                        Exemplo: {'T2': [('T1', 'x')], 'T3': [('T1', 'y')]}

        Example:
            waits = {'T2': [('T1', 'x')], 'T3': [('T1', 'y')]}
            A função irá adicionar as arestas ('T2', 'T1') e ('T3', 'T1') ao grafo.
        """

        for transacao_bloqueada, dependencias in waits.items():
            for transacao_bloqueante, _ in dependencias:
                self.graph.add_edge(f'T{transacao_bloqueada}', f'T{transacao_bloqueante}')
        