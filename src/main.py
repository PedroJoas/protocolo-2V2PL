from util.transactionParser import Parser
from util.locks import Locks


schedule = input('Digite o schedule: ')
print('--'*20)
parser = Parser(schedule)

schedule_parsed = parser.parser_schedule()

locks = Locks()

locks.add_locks(schedule_parsed)

print(locks.retorna_new_schedule())

print(locks.__getattribute__('waits'))

