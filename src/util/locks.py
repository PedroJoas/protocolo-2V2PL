from collections import defaultdict
from typing import Any
import re

import networkx as nx

class Locks:

    def __init__(self) -> None:
        self.new_schedule = []
        self.graph = nx.DiGraph()
    
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
        elif operacao == 'compartilhado':
            return 'r'
        elif operacao == 'exclusivo':
            return 'w'          
        else:
            raise ValueError(f"Operação inválida.")
    
    def _add_to_waits(self, transacao_bloqueada, wait_info):
        transacao_bloqueante, tipo_operacao, objeto = wait_info

        # Adiciona a aresta temporariamente para verificar ciclos
        self.graph.add_edge(f'T{transacao_bloqueada}', f'T{transacao_bloqueante}')

        # Verifica se a adição cria um ciclo
        if self._detect_deadlock():
            self.graph.remove_edge(f'T{transacao_bloqueada}', f'T{transacao_bloqueante}')
            return False  # Indica que um deadlock foi detectado

        # Garantir que a chave existe antes de adicionar
        if transacao_bloqueada not in self.waits:
            self.waits[transacao_bloqueada] = []

        # Se não há ciclo, adiciona à espera
        self.waits[transacao_bloqueada].append((transacao_bloqueante, tipo_operacao, objeto))
        return True

    def _detect_deadlock(self):
        """Verifica se há ciclos no grafo de espera."""
        try:
            nx.find_cycle(self.graph, orientation='original')
            print("Ciclo encontrado!")
            return True
        except nx.NetworkXNoCycle:
            return False

    def add_locks(self, schedule_parsed: list) -> None:
        """
        Adiciona locks às transações com base em um cronograma de operações.

        Esta função processa uma lista de comandos representando transações e suas operações 
        (como commits ou pedidos de locks) e atualiza a estrutura de locks e a fila de espera 
        conforme as regras de bloqueio para locks compartilhados e exclusivos.

        Parâmetros:
        -----------
        schedule_parsed : list
            Uma lista de comandos onde cada comando é uma tupla contendo:
            - transação (str): Identificador da transação (ex: 'T1').
            - operação (str): Tipo de operação ('c' para commit, 'r' para lock compartilhado, 
            'w' para lock exclusivo).
            - objeto (str ou None): O objeto sobre o qual a operação é realizada.

        Retorna:
        --------
        None
        """

        locks = defaultdict(lambda: defaultdict(list))

        waits =  defaultdict(list)
        
        for command in schedule_parsed:
            if command[1] == 'c':
                self._process_commit(command)

            else:
                transacao = command[0]
                tipo_operacao = self._type_lock(command[1])
                objeto = command[2]

                if objeto not in locks.keys():

                    locks[objeto][tipo_operacao].append(transacao)
                    self._add_new_schedule(command) # Adiciona no novo schedule

                elif tipo_operacao == 'compartilhado':

                    if len(locks[objeto]['exclusivo']) == 0:
                        locks[objeto][tipo_operacao].append(transacao)
                        self._add_new_schedule(command)
                    else:
                        transacao_lock = locks[objeto]['exclusivo']
                        if not self._add_to_waits(transacao, (transacao_lock[0], 'exclusivo', objeto)):
                            print(f"Deadlock detectado ao adicionar {transacao} à espera.")
            
                        

                elif tipo_operacao == 'exclusivo':

                    if (len(locks[objeto]['exclusivo']) == 0 and len(locks[objeto]['compartilhado']) == 0):
                        locks[objeto][tipo_operacao].append(transacao)
                        self._add_new_schedule(command)

                    elif (len(locks[objeto]['compartilhado']) == 1) and (transacao in locks[objeto]['compartilhado']): # Aplicando update lock
                        locks[objeto]['exclusivo'] = locks[objeto]['compartilhado']
                        locks[objeto]['compartilhado'] = []
                        self._add_new_schedule(command)

                else:
                    transacao_lock = locks[objeto]['exclusivo'] + locks[objeto]['compartilhado']
                    if not self._add_to_waits(transacao, (transacao_lock[0], tipo_operacao, objeto)):
                        print(f"Deadlock detectado ao adicionar {transacao} à espera.")



            self.locks = {k: dict(v) for k, v in locks.items()}
            self.waits = dict(waits)

    def _add_new_schedule(self,command: tuple) -> None:
        """
        Adiciona um novo comando ao cronograma reformulado.

        Esta função recebe um comando na forma de uma tupla, extrai as informações relevantes 
        (identificador da transação, tipo de operação e objeto), e formata um novo comando que 
        é adicionado à lista de cronograma reformulado.

        Parâmetros:
        -----------
        command : tuple
            Uma tupla representando um comando, que contém:
            - transação (str): Identificador da transação (ex: 'T1').
            - operação (str): Tipo de operação ('c' para commit, 'r' para lock compartilhado, 
            'w' para lock exclusivo).
            - objeto (str ou None): O objeto sobre o qual a operação é realizada.

        Retorna:
        --------
        None
        """

        transacao = re.sub('[^0-9]','',command[0])
        tipo_operacao = command[1]
        objeto = command[2]
        if tipo_operacao == 'c':
            refactor_command = f'{tipo_operacao}{transacao}'
        else:
            refactor_command = f'{tipo_operacao}{transacao}({objeto})'

        self.new_schedule.append(refactor_command)
    
    def retorna_new_schedule(self):
        return ''.join(self.new_schedule)

    def _process_commit(self, command):
        """
        Processa um commit de transação, atualizando o cronograma e liberando locks.

        Esta função é chamada quando uma transação realiza um commit. Ela adiciona o comando 
        de commit ao cronograma reformulado e remove todos os locks associados à transação, 
        liberando os objetos que estavam bloqueados.

        Parâmetros:
        -----------
        command : tuple
            Uma tupla representando o comando de commit, que contém:
            - transação (str): Identificador da transação (ex: 'T1').
            - operação (str): Tipo de operação, que deve ser 'c' para commit.
            - objeto (str ou None): O objeto sobre o qual a operação é realizada (não utilizado para commit).

        Retorna:
        --------
        None
        """

        transacao = command[0]

        # Adiciona o commit ao novo schedule
        self._add_new_schedule(command)

        # Libera todos os locks associados a essa transação
        for obj, tipos_locks in self.locks.items():
            # Remove a transação dos locks compartilhados e exclusivos
            if 'compartilhado' not in tipos_locks:
                tipos_locks['compartilhado'] = []
            if 'exclusivo' not in tipos_locks:
                tipos_locks['exclusivo'] = []
            
            if transacao in tipos_locks['compartilhado']:
                tipos_locks['compartilhado'].remove(transacao)
            if transacao in tipos_locks['exclusivo']:
                tipos_locks['exclusivo'].remove(transacao)

            self._libera_lock(obj, tipos_locks)

        
        


    def _libera_lock(self, objeto, tipos_locks):
        """
        Libera um lock de um objeto e concede locks a transações em espera.

        Esta função é chamada quando um objeto é liberado. Ela verifica se há transações que estão 
        esperando pelo objeto liberado e tenta conceder os locks apropriados a essas transações, 
        atualizando o cronograma conforme necessário.

        Parâmetros:
        -----------
        objeto : str
            O objeto cujo lock está sendo liberado.

        tipos_locks : dict
            Um dicionário contendo os tipos de locks (compartilhado e exclusivo) associados ao 
            objeto, representando as transações que possuem esses locks.

        Retorna:
        --------
        None
        """

        transacoes_a_remover = []

        # Verifica se há transações esperando por esse objeto
        for trans_esperando, objeto_esperado in self.waits.items():
        # Se a transação está esperando pelo objeto que foi liberado, tenta conceder o lock
            if objeto == objeto_esperado[0][2]:  # Verifica se o objeto esperado é o mesmo que foi liberado
                        # Verifica se o lock pode ser concedido
                if len(tipos_locks['exclusivo']) == 0 and (len(tipos_locks['compartilhado']) == 0 or objeto_esperado[0][0] == 'compartilhado'):
                # Concede o lock à transação esperando
                    tipo_operacao = objeto_esperado[0][1]
                    self.locks[objeto][tipo_operacao].append(trans_esperando)

                    # Adiciona à lista de transações que terão o lock concedido
                    transacoes_a_remover.append(trans_esperando)

                    # Adiciona ao novo schedule
                    tipo_operacao_espera = self._type_lock(objeto_esperado[0][1])
                    self._add_new_schedule((trans_esperando, tipo_operacao_espera, objeto))
                    

        for trans_esperando in transacoes_a_remover:
            #self.waits.pop(trans_esperando)
            del self.waits[trans_esperando]
            
            
    


