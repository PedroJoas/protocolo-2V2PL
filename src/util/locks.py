from collections import defaultdict

class Locks:

    def _type_lock(self,operacao: str) -> str:
        # Docstring gerada pelo chat gpt
        """
        Determina o tipo de bloqueio com base na operação fornecida.

        Args:
            operacao (str): Uma string representando a operação. 
                            Deve ser 'r' para leitura ou 'w' para escrita.

        Returns:
            str: O tipo de bloqueio associado à operação:
                - 'compartilhado' para operações de leitura ('r')
                - 'exclusivo' para operações de escrita ('w')

        Raises:
            ValueError: Se a operação fornecida não for 'r' ou 'w'.
        """

        if operacao == 'r':
            return 'compartilhado'
        elif operacao == 'w':
            return 'exclusivo'
        else:
            raise ValueError(f"Operação inválida.")
    

    def add_locks(self, schedule: dict) -> dict:
        # Docstring gerada pelo chat gpt
        """
        Adiciona bloqueios e determina a ordem de espera entre transações.

        Este método recebe um dicionário de operações de transações (schedule) e 
        retorna dois dicionários: 
        - `locks`: que mapeia os objetos bloqueados e suas transações associadas.
        - `waits`: que registra quais transações estão esperando por outros bloqueios.

        Args:
            schedule (dict): Um dicionário contendo as transações e suas operações. 
                            O formato esperado é:
                            {transacao: [(operacao, objeto)]}, onde:
                            - `transacao` (str) é o identificador da transação (ex: 'T1').
                            - `operacao` (str) é 'r' (leitura) ou 'w' (escrita).
                            - `objeto` (str) é o recurso sendo acessado (ex: 'x', 'y').

        Returns:
            tuple[dict, dict]: 
                - `locks`: Um dicionário onde cada objeto é a chave e o valor é um 
                outro dicionário que mapeia os tipos de bloqueio ('compartilhado' ou 
                'exclusivo') para as transações associadas.
                Exemplo: {'x': {'compartilhado': ['T1'], 'exclusivo': []}}
                
                - `waits`: Um dicionário que mapeia cada transação para uma lista de tuplas, 
                onde cada tupla contém a transação bloqueante e o objeto que causou o bloqueio.
                Exemplo: {'T2': [('T1', 'x')]}

        Raises:
            ValueError: Se a operação fornecida não for válida ('r' ou 'w') no método `_type_lock`.
        """    

        locks = defaultdict(lambda: defaultdict(list))


        waits =  defaultdict(list)

        for transacoes in schedule.items(): # {T1:[('r', 'y')]...}
            transacao = transacoes[0]
            operacoes = transacoes[1] # lista de operações de cada transação

            for processo in operacoes:

                operacao = processo[0] # Operação da transação(read(r) or write(w))
                objeto = processo[1] # Objeto que está sendo acessado pela operação
                tipo_operacao = self._type_lock(processo[0])

                if objeto not in locks.keys():
                    locks[objeto][tipo_operacao].append(transacao)

                elif tipo_operacao == 'compartilhado':

                    if len(locks[objeto]['exclusivo']) == 0:
                        locks[objeto][tipo_operacao].append(transacao)

                    else:
                        transacao_lock = locks[objeto]['exclusivo']
                        waits[transacao].append((transacao_lock[0], objeto)) # [0] serve para tirar a camada superior da lista. [[1]] depois fica [1

                elif tipo_operacao == 'exclusivo':
                    
                    if (len(locks[objeto]['exclusivo']) == 0 and len(locks[objeto]['compartilhado']) == 0):
                        locks[objeto][tipo_operacao].append(transacao)

                    elif (len(locks[objeto]['compartilhado']) == 1) and (transacao in locks[objeto]['compartilhado']): # Aplicando update lock
                        locks[objeto]['exclusivo'] = locks[objeto]['compartilhado']
                        locks[objeto]['compartilhado'] = []

                    else:
                        transacao_lock = locks[objeto]['exclusivo'] + locks[objeto]['compartilhado']
                        waits[transacao].append((transacao_lock[0], objeto)) # [0] serve para tirar a camada superior da lista. [[1]] depois fica [1]
                    # waits receber uma tupla com a transacao do block e o objeto
                
            
                


        locks = {k: dict(v) for k, v in locks.items()}
        waits = dict(waits)

        return locks, waits
