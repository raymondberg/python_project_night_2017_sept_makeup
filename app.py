from __future__ import unicode_literals
from statistics import median
import sys

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
import meetup.api

def get_names():
    client = meetup.api.Client('3f6d3275d3b6314e73453c4aa27')

    rsvps=client.GetRsvps(event_id='239174106', urlname='_ChiPy_')
    member_id = ','.join([str(i['member']['member_id']) for i in rsvps.results])
    members = client.GetMembers(member_id=member_id)

    names = []
    for member in members.results:
        try:
            names.append(member['name'])
        except:
            pass # ignore those who do not have a complete profile

    return names

command_completer = WordCompleter(['add', 'show'] + get_names(), ignore_case=True)

class TeamBuilder:
    def __init__(self, user_dict):
        self.user_dict = user_dict

    def execute(self, command):
        tokens = command.split(' ') ## TODO: Handle trailing spaces

        if tokens[0] == 'add' and len(tokens) > 2:
            name = " ".join(tokens[1:-1])
            number = tokens[-1]
            return self.add(name, number)
        if tokens[0] == 'list':
            return self.show_list()
        if tokens[0] == 'group':
            return self.group()
        return "You issued:" + command

    def add(self, name, number):
        try:
            safe_number = int(number)
        except ValueError:
            return "Invalid number: {}".format(number)
        self.user_dict[name] = safe_number
        return self.user_dict

    def show_list(self):
        total_ppl = len(user_dict)
        median_line = median(user_dict.values()) if total_ppl != 0 else 0
        return "Total People: {}\nMedian Lind Count: {}".format(total_ppl, median_line)

    def group(self):
        sorted_tuples = sorted([ (value, name) for name,value in self.user_dict.items() ])

        groups = []

        while len(sorted_tuples) > 0:
            group = []
            pick_from_bottom = True
            while len(sorted_tuples) > 0 and len(group) < 4:
                group.append(sorted_tuples.pop(0)[1] if pick_from_bottom else sorted_tuples.pop()[1])
                pick_from_bottom = not pick_from_bottom
            groups.append(group)

        return "\n".join(["Group: {}".format(', '.join([person for person in group])) for group in groups])

## Feature 1: Add command
## Feature 2: List command
## Feature 3: Group command

def main(team_builder):
    history = InMemoryHistory()

    while True:
        try:
            text = prompt('> ',
                          completer = command_completer,
                          history=history,
                          on_abort=AbortAction.RETRY)
            message = team_builder.execute(text)

            print(message)
        except EOFError:
            break  # Control-D pressed.

    print('GoodBye!')

if __name__ == '__main__':
    user_dict = {}
    team_builder = TeamBuilder(user_dict)
    main(team_builder)
