from copy import deepcopy
import shlex
import click
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter

from .prompt_validators import ChoiceValidator


class ObjectPrompt(object):
    def __init__(self, child_key, pre_prompt_message=None, *args, **kwargs):
        self.pre_prompt_message = pre_prompt_message
        # property of child that the user will select by
        self.child_key = child_key
        self.children = []

    def get_children(self, *args, **kwargs):
        raise NotImplementedError

    def get_child_object_prompt(self, child, *args, **kwargs):
        raise NotImplementedError

    def overview(self, refresh, *args, **kwargs):
        raise NotImplementedError

    def command_prompt(self, ctx, default_subcommand=None):
        # get the children if being run for the first time
        # - if empty and supposed to be, then this won't hurt
        if not self.children:
            self.children = self.get_children()

        self.overview(refresh=False)

        user_input = None
        while user_input != 'done':

            click.echo('')
            if self.pre_prompt_message:
                click.echo(self.pre_prompt_message)

            commands = set(ctx.command.commands.keys())
            commands.add('help')
            commands.add('done')

            commands = list(commands)

            choices = [str(x[self.child_key]) for x in self.children]
            user_input = prompt(
                u'> ',
                completer=WordCompleter(choices + commands),
                validator=ChoiceValidator(choices, commands=commands, allow_empty=True),
            )

            if user_input == '':
                if default_subcommand:
                    for child in self.children:
                        self.interpret_subcommand(ctx, default_subcommand + ' ' + str(child[self.child_key]))
                break
            elif user_input == 'done':
                break
            elif shlex.split(user_input)[0] == 'help':
                # print the help ourselves
                click.echo('Available commands:')
                for command in commands:
                    click.echo('  ' + command)

            elif shlex.split(user_input)[0] in commands:
                self.interpret_subcommand(ctx, user_input)
            elif default_subcommand:
                # assume they started with repo name or pr number, accept as ok
                # behavior given where they're at
                self.interpret_subcommand(ctx, default_subcommand + ' ' + user_input)

            # self.overview(refresh=True)

    def interpret_subcommand(self, ctx, user_input):
        parts = shlex.split(user_input)
        command_name = parts[0]
        arg_parts = parts[1:]
        subcommand = ctx.command.commands[command_name]
        try:
            subcommand.main(args=arg_parts, parent=ctx, standalone_mode=False)
        except TypeError as e:
            click.secho('Type error. You probably used the arguments/options incorrectly.', fg='red')
            click.secho(str(e), fg='red')
