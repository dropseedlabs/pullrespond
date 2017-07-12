import shlex

import click
import click._bashcomplete
from prompt_toolkit.completion import Completer, Completion


class ClickCompleter(Completer):
    def __init__(self, ctx, additional_choices, default_subcommand=None, choice_display_meta=None):
        self.ctx = ctx
        self.additional_choices = additional_choices
        self.default_subcommand = default_subcommand
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
                elif self.default_subcommand and first_arg in self.additional_choices:
                    # if we entered an argument for the default subcommand
                    current_command = current_command = current_command.commands[self.default_subcommand]

        choices = []

        for param in current_command.params:
            if isinstance(param, click.Option):
                for options in (param.opts, param.secondary_opts):
                    for o in options:
                        choices.append(Completion(o, -len(incomplete),
                                                  display_meta=param.help))

        if isinstance(current_command, click.MultiCommand):
            for name, command in current_command.commands.items():
                choices.append(Completion(
                    name,
                    -len(incomplete),
                    display_meta=command.short_help,
                ))

        if len(args) < 1:
            choices += [
                Completion(x, -len(incomplete), display_meta=self.choice_display_meta)
                for x in self.additional_choices
            ]

        for item in choices:
            if item.text.startswith(incomplete):
                yield item
