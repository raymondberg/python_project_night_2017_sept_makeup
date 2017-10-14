from __future__ import unicode_literals
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
        tokens = command.split(' ')

        if tokens[0] == 'add' and len(tokens) > 2:
            name = " ".join(tokens[1:-1])
            number = tokens[-1]
            return self.add(name, number)
        return "You issued:" + command

    def add(self, name, number):
        try:
            safe_number = int(number)
        except ValueError:
            return "Invalid number: {}".format(number)
        self.user_dict[name] = safe_number
        return self.user_dict

## Feature 1: Add command

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
