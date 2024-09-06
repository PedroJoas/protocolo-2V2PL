import re
from collections import defaultdict


class Parser:

    def __init__(self, schedule) -> None:
        self.schedule = schedule

    def parser_schedule(self):
        schedule_parsed = self.schedule.strip().split(',')

        processes = defaultdict(list)

        for process in schedule_parsed:
        # Regex para capturar a letra, o número e o objeto
            pattern = r'([a-zA-Z])(\d+)\(([^)]+)\)'

            # Encontrar correspondências
            match = re.match(pattern, process)

            if match:
                operation = match.group(1)
                number = match.group(2)
                object = match.group(3)
                processes[f'T{number}'].append((operation, object))
            else:
                print('Não corresponde ao padrão')
        return processes
