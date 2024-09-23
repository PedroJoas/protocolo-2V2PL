import re
from collections import defaultdict


class Parser:

    def __init__(self, schedule:str) -> None:
        self.schedule = schedule

    def parser_schedule(self) -> list:
        """
        Analisa uma string de cronograma e a transforma em uma lista de comandos estruturados.

        Esta função processa um cronograma de transações em formato de string, extrai informações 
        sobre operações e as organiza em uma lista de tuplas. Cada tupla representa um comando 
        com a transação, o tipo de operação e o objeto relacionado.

        Retorna:
        --------
        list
            Uma lista de tuplas, onde cada tupla contém a transação (como 'T1'), o tipo de 
            operação (como 'r' ou 'w'), e o objeto relacionado (ou None, se for um commit).
        """
        pattern = r'([a-zA-Z])(\d+)([a-zA-Z])| ([a-zA-Z])(\d+)'
        self.schedule = re.sub(r'(c\d+)', r'\1)', self.schedule)

        schedule_list = [command.replace('(', '') for command in self.schedule.split(')') if command] # if command serve para apenas pegar os objetos não vazios
        schedule_parsed = []

        for command in schedule_list:
            match = re.match(pattern, command)

            if 'c' in command:
                op = command[0]
                transacao = command[1]
                objeto = None

            elif match:
                op = match.group(1)
                transacao = match.group(2)
                objeto = match.group(3)

            schedule_parsed.append((f'T{transacao}', op, objeto))


        return schedule_parsed
