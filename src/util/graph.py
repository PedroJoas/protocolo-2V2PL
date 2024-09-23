import networkx as nx
import plotly.graph_objects as go

class Graph:

    def __init__(self, graph) -> None:
        self.graph = graph
    

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
        

    # Função para desenhar o grafo com setas
    def draw_graph(G):
        pos = nx.spring_layout(G)  # Layout dos nós

        # Cria uma lista de trace para as arestas (com setas)
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Trace para a linha com uma seta (arrowstyle)
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=2, color='cornflowerblue'),
                    hoverinfo='none',
                    marker=dict(size=5, color='red')  # Apenas para visualização clara
                )
            )

        # Cria trace para os nós
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            text=[f'Processo {node}' for node in G.nodes()],
            mode='markers+text',
            textposition='top center',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='lightblue',
                size=30,
                line_width=2
            )
        )

        # Configuração de layout com setas nas arestas
        fig = go.Figure(data=edge_trace + [node_trace],
                        layout=go.Layout(
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=0),
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False),
                            annotations=[
                                dict(
                                    ax=pos[edge[0]][0],
                                    ay=pos[edge[0]][1],
                                    x=pos[edge[1]][0],
                                    y=pos[edge[1]][1],
                                    xref='x', yref='y', axref='x', ayref='y',
                                    showarrow=True,
                                    arrowhead=3,  # Define o tipo da seta
                                    arrowsize=1.5,
                                    arrowwidth=2,
                                    arrowcolor='cornflowerblue'
                                ) for edge in G.edges()
                            ]
                        ))

        return fig

