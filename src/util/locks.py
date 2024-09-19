from collections import defaultdict
from typing import Any

class Locks:

    def __init__(self) -> None:
        self.new_schedule = []

    
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
                
            
                


        self.locks = {k: dict(v) for k, v in locks.items()}
        self.waits = dict(waits)


    def _release_locks(self, transacao: str, schedule_original: dict) -> None:
        """
        Libera todos os bloqueios mantidos por uma transação específica e adiciona operações ao novo schedule.
        
        Args:
            transacao (str): A transação que está liberando seus bloqueios.
            locks (dict): O dicionário que contém os bloqueios ativos. 
                        Formato: {objeto: {'compartilhado': [transacoes], 'exclusivo': [transacoes]}}.
            waits (dict): O dicionário que contém as transações que estão esperando pelos bloqueios.
                        Formato: {transacao: [(transacao_bloqueante, objeto)]}.
            self.new_schedule (list): Lista que armazena as operações liberadas após a liberação dos bloqueios.
                                Cada entrada será no formato ('operação_numero(objeto)').
            schedule_original (dict): O dicionário que contém o schedule original para obter as operações da transação.
        
        Returns:
            None
        """

        # Para cada objeto bloqueado pela transação
        for objeto, tipos_bloqueio in self.locks.items():
            
            # Garantir que 'compartilhado' e 'exclusivo' estejam sempre presentes como listas vazias
            if 'compartilhado' not in tipos_bloqueio:
                tipos_bloqueio['compartilhado'] = []
            if 'exclusivo' not in tipos_bloqueio:
                tipos_bloqueio['exclusivo'] = []

            # Remover a transação dos bloqueios compartilhados
            if transacao in tipos_bloqueio['compartilhado']:
                tipos_bloqueio['compartilhado'].remove(transacao)
                self.new_schedule.append(f'unlock_shared{transacao[1]}({objeto})')  # Adiciona ao novo scheduler

            # Remover a transação dos bloqueios exclusivos
            if transacao in tipos_bloqueio['exclusivo']:
                tipos_bloqueio['exclusivo'].remove(transacao)
                self.new_schedule.append(f'unlock_exclusive{transacao[1]}({objeto})')  # Adiciona ao novo scheduler

            # Checar se há transações esperando por esse bloqueio
            for waiting_transacao, blocked_objeto in list(self.waits.items()):
                for transacao_blocking, obj in blocked_objeto:
                    if obj == objeto and transacao_blocking == transacao:
                        # Transação que estava esperando agora pode adquirir o bloqueio
                        self.waits[waiting_transacao] = [(t, o) for t, o in self.waits[waiting_transacao] if o != objeto]  # Remove o bloqueio liberado
                        
                        # Buscar a operação original (leitura ou escrita) do schedule original
                        for operacao, obj in schedule_original[waiting_transacao]:
                            if obj == objeto:
                                tipo_operacao = 'r' if operacao == 'r' else 'w'
                                break
                        
                        # Adicionar a transação esperando ao novo schedule
                        self.new_schedule.append(f'{tipo_operacao}{waiting_transacao[1]}({objeto})')

                        # Agora adicionar o bloqueio que a transação waiting estava esperando
                        tipo_operacao = 'compartilhado' if tipo_operacao == 'r' else 'exclusivo'
                        self.locks[objeto][tipo_operacao].append(waiting_transacao)
                        
            # Remove entradas vazias
            self.waits = {k: v for k, v in self.waits.items() if v}
        
        # Remove entradas de bloqueios vazios
        self.locks = {k: v for k, v in self.locks.items() if v['compartilhado'] or v['exclusivo']}
    
    def liberar_todos_bloqueios(self, schedule_original: dict) -> None:
        """
        Libera todos os bloqueios de todas as transações ativas e atualiza o novo schedule,
        incluindo as operações antes de desbloquear.

        Args:
            transacoes_ativas (list): Lista de transações ativas.
            locks (dict): O dicionário que contém os bloqueios ativos.
            waits (dict): O dicionário que contém as transações que estão esperando pelos bloqueios.
            new_schedule (list): Lista que armazena as operações liberadas após a liberação dos bloqueios.
            schedule_original (dict): O dicionário que contém o schedule original para obter as operações da transação.

        Returns:
            None
        """

        # Itera sobre cada transação ativa e libera seus bloqueios
        for transacao in schedule_original.keys():
            # Adiciona as operações da transação ao novo schedule
            for operacao, objeto in schedule_original[transacao]:
                self.new_schedule.append(f"{operacao}{transacao[1]}({objeto})")
            
            # Chama a função para liberar os bloqueios da transação
            self._release_locks(transacao, schedule_original)
        
        # Mostra os resultados finais
        print("Novo schedule:", self.new_schedule)
        print('--'*20)
        print("Bloqueios restantes:", self.locks)
        print('--'*20)
        print("Transações esperando:", self.waits)
        print('--'*20)
    

    def __getattribute__(self, name_attr: str) -> Any:
        return super().__getattribute__(name_attr)  # Evita loop infinito



