import re
from collections import defaultdict


class Parser:

    def __init__(self, schedule) -> None:
        self.schedule = schedule

    def parser_schedule(schedule):
        pattern = r'([a-zA-Z])(\d+)([a-zA-Z])'

        schedule_list = [command.replace('(', '') for command in schedule.split(')')]
        schedule_list.pop()
        schedule_parsed = []

        for command in schedule_list:
            match = re.match(pattern, command)

            if match:
                op = match.group(1)
                transacao = match.group(2)
                objeto = match.group(3)

                schedule_parsed.append((f'T{transacao}', op, objeto))


            return schedule_parsed
