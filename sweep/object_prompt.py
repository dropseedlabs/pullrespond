import click
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter

from .prompt_validators import ChoiceValidator


class ObjectPrompt(object):
    def __init__(self, commands, child_key, pre_prompt_message=None, *args, **kwargs):
        self.commands = commands + ['overview', 'done']
        self.pre_prompt_message = pre_prompt_message
        # property of child that the user will select by
        self.child_key = child_key
        self.children = self.get_children()

    def get_children(self, *args, **kwargs):
        raise NotImplementedError

    def get_child_object_prompt(self, child, *args, **kwargs):
        raise NotImplementedError

    def overview(self, refresh, *args, **kwargs):
        raise NotImplementedError

    def done(self, *args, **kwargs):
        pass

    def command_prompt(self):
        self.overview(refresh=False)

        user_input = None
        while user_input != 'done':

            click.echo('')
            if self.pre_prompt_message:
                click.echo(self.pre_prompt_message)

            choices = [str(x[self.child_key]) for x in self.children]
            user_input = prompt(
                u'> ',
                completer=WordCompleter(choices + self.commands),
                validator=ChoiceValidator(choices, commands=self.commands, allow_empty=True),
            )

            if user_input == '':
                for child in self.children:
                    child_prompt = self.get_child_object_prompt(child[self.child_key])
                    child_prompt.command_prompt()
                # exit the while loop by returning when done
                return
            elif user_input.split()[0] in self.commands:
                parts = user_input.split()
                command = parts[0]
                # join them back as 1 string
                args = [' '.join(parts[1:])]
                getattr(self, command)(*args)
            else:
                click.secho('Getting {} {}...'.format(self, user_input), fg='yellow')
                child_prompt = self.get_child_object_prompt(user_input)
                child_prompt.command_prompt()

            self.overview(refresh=True)
