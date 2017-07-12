import shlex
import click
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from .prompt_completers import ClickCompleter


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

        prompt_memory_history = InMemoryHistory()

        user_input = None
        while user_input != 'done':

            click.echo('')
            if self.pre_prompt_message:
                click.echo(self.pre_prompt_message)

            commands = [
                ('done', 'Close this prompt'),
            ]
            choices = [str(x[self.child_key]) for x in self.children]

            user_input = prompt(
                u'> ',
                completer=ClickCompleter(
                    ctx,
                    additional_commands=commands,
                    default_subcommand=default_subcommand,
                    default_subcommand_choices=choices,
                    choice_display_meta='(enter prompt)'
                ),
                history=prompt_memory_history,
            )

            if user_input == '':
                click.secho('Enter a command.', fg='red')
            elif user_input == 'done':
                break
            elif default_subcommand and shlex.split(user_input)[0] in choices:
                # assume they started with repo name or pr number, accept as ok
                # behavior given where they're at
                self.interpret_subcommand(ctx, default_subcommand + ' ' + user_input)

                # if entered a new prompt (no args, just choice),
                # when we come back out, reload the overview
                if len(shlex.split(user_input)) == 1:
                    self.overview(refresh=True)
            else:
                self.interpret_subcommand(ctx, user_input)

            # self.overview(refresh=True)

    def interpret_subcommand(self, ctx, user_input):
        parts = shlex.split(user_input)
        command_name = parts[0]
        arg_parts = parts[1:]
        subcommand = ctx.command.commands.get(command_name, None)

        if subcommand is None:
            click.secho('"{}" command not found.'.format(command_name), fg='red')
            return

        try:
            subcommand.main(args=arg_parts, parent=ctx, standalone_mode=False)
        except TypeError as e:
            click.secho('Type error. You probably used the arguments/options incorrectly.', fg='red')
            click.secho(str(e), fg='red')
