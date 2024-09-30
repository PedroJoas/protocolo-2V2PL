from collections import defaultdict
import re

class Locks:
    def __init__(self) -> None:
        self.schedule_escalonado = []
    def _type_lock(self, operador):
         
        if operador == 'r':
            return 'leitura'
        elif operador == 'w':
            return 'escrita'
        elif operador == 'c':
            return 'commit'
        else:
            raise ValueError(f'Operação {operador} inválida!')
    def add_locks(self, schedule_parsed: list) -> None:
            """
            Adiciona locks às transações com base em um cronograma de operações.
            """
            
            locks = defaultdict(lambda: defaultdict(list))
            waits = defaultdict(list)

            for operacao in schedule_parsed:
                transacao = operacao[0]
                tipo_operacao = self._type_lock(operacao[1])
                objeto = operacao[2]

                # Lógica para operação do tipo leitura
                if tipo_operacao == 'leitura':
                     
                    if (objeto not in locks.keys()) or (not locks[objeto]['certify']):
                        locks[objeto][tipo_operacao].append(transacao)
                        self._add_new_schedule(operacao)

                    else:
                        transacao_bloqueio = locks[objeto]['certify'][0]
                        waits[transacao_bloqueio].append(operacao)

                # Lógica para operação do tipo leitura
                if tipo_operacao == 'escrita':
                    
                    if (objeto not in locks.keys()) or (not locks[objeto]['certify']) or (not locks[objeto]['escrita']):
                        locks[objeto][tipo_operacao].append(transacao)
                        self._add_new_schedule(operacao)

                    else:
                        if locks[objeto]['certify']:
                            transacao_bloqueio = locks[objeto]['certify'][0]
                        else:
                            transacao_bloqueio = locks[objeto]['escrita'][0]
                        
                        waits[transacao_bloqueio].append(operacao)

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

        self.schedule_escalonado.append(refactor_command)

            
