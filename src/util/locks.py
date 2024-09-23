from collections import defaultdict
from typing import Any
import re
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
        elif operacao == 'compartilhado':
            return 'r'
        elif operacao == 'exclusivo':
            return 'w'          
        else:
            raise ValueError(f"Operação inválida.")
    

    def add_locks(self, schedule_parsed: list) -> None:
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
                        waits[transacao].append((transacao_lock[0], tipo_operacao,objeto)) # Adicionando na espera

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
                    waits[transacao].append((transacao_lock[0], tipo_operacao, objeto)) 
                    print(f'Adicionado {transacao_lock[0]} no waits')


            self.locks = {k: dict(v) for k, v in locks.items()}
            self.waits = dict(waits)

    def _add_new_schedule(self,command: tuple) -> None:

        transacao = re.sub('[^0-9]','',command[0])
        tipo_operacao = command[1]
        objeto = command[2]
        if tipo_operacao == 'c':
            refactor_command = f'{tipo_operacao}{transacao}'
        else:
            refactor_command = f'{tipo_operacao}{transacao}({objeto})'

        self.new_schedule.append(refactor_command)
        

    def _process_commit(self, command):
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
                    
                    # Adiciona ao novo schedule
                    tipo_operacao_espera = self._type_lock(objeto_esperado[0][1])
                    self._add_new_schedule((trans_esperando, tipo_operacao_espera, objeto))
                    

        for trans_esperando in transacoes_a_remover:
            del self.waits[trans_esperando]
            
    


