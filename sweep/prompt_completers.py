import shlex

import click
import click._bashcomplete
from prompt_toolkit.completion import Completer, Completion


class ClickCompleter(Completer):
    def __init__(self, ctx, additional_commands=[], default_subcommand=None, default_subcommand_choices=None, choice_display_meta=None):
        self.ctx = ctx
        self.additional_commands = additional_commands
        self.default_subcommand = default_subcommand
        self.default_subcommand_choices = default_subcommand_choices
        self.choice_display_meta = choice_display_meta

    def get_completions(self, document, complete_event=None):
        # Code analogous to click._bashcomplete.do_complete

        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return

        cursor_within_command = \
            document.text_before_cursor.rstrip() == document.text_before_cursor

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ''

        current_command = self.ctx.command

        # we want to drill down the commands to get prompts
        # relative to the last full command we notice
        reversed_args = args[::-1]
        while len(reversed_args) > 0:
            first_arg = reversed_args.pop()  # pop one off
            # if the last one was a multicommand, see if this is a subcommand of it
            if isinstance(current_command, click.MultiCommand):
                if first_arg in current_command.commands.keys():
                    current_command = current_command.commands[first_arg]
                elif self.default_subcommand and first_arg in self.default_subcommand_choices:
                    # if we entered an argument for the default subcommand
                    current_command = current_command = current_command.commands[self.default_subcommand]

        choices = []

        # add staticly available commands if no args yet
        if len(args) < 1 and self.additional_commands:
            choices += [
                Completion(command, -len(incomplete), display_meta=display_meta)
                for command, display_meta in self.additional_commands
            ]

        # add --option completions
        for param in current_command.params:
            if isinstance(param, click.Option):
                for options in (param.opts, param.secondary_opts):
                    for o in options:
                        display_meta = '{help}. Default: {default}'.format(
                            help=param.help,
                            default=param.default,
                        )
                        choices.append(Completion(o, -len(incomplete),
                                                  display_meta=display_meta))

        # add subcommand completions
        if isinstance(current_command, click.MultiCommand):
            for name, command in current_command.commands.items():
                choices.append(Completion(
                    name,
                    -len(incomplete),
                    display_meta=command.short_help,
                ))

        # add choices for default subcommand
        if len(args) < 1 and self.default_subcommand_choices:
            choices += [
                Completion(x, -len(incomplete), display_meta=self.choice_display_meta)
                for x in self.default_subcommand_choices
            ]

        # yield all our completions
        for item in choices:
            if item.text.startswith(incomplete):
                yield item
