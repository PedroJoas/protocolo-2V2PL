from collections import defaultdict

class Locks:

    def _type_lock(self,operacao):
        if operacao == 'r':
            return 'compartilhado'
        elif operacao == 'w':
            return 'exclusivo'
        else:
            raise ValueError(f"Operação inválida.")
    

    def add_locks(self,schedule):
        "Recebe o schedule parsed. Retornar os dicionários locks e waits"
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

                elif tipo_operacao == 'compartilhado' and len(locks[objeto]['exclusivo']) == 0:
                    locks[objeto][tipo_operacao].append(transacao)

                elif tipo_operacao == 'exclusivo' and (len(locks[objeto]['exclusivo']) == 0 and len(locks[objeto]['compartilhado']) == 0):
                    locks[objeto][tipo_operacao].append(transacao)

                elif tipo_operacao == 'compartilhado':
                    transacao_lock = locks[objeto]['exclusivo']
                    waits[transacao].append(transacao_lock[0]) # [0] serve para tirar a camada superior da lista. [[1]] depois fica [1]

                else:
                    transacao_lock = locks[objeto]['exclusivo'] + locks[objeto]['compartilhado']
                    waits[transacao].append(transacao_lock[0]) # [0] serve para tirar a camada superior da lista. [[1]] depois fica [1]
                
                    


        locks = {k: dict(v) for k, v in locks.items()}
        waits = dict(waits)

        return locks, waits
