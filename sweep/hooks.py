from os import path
from subprocess import check_call

import click


def run_hook(name, *args):
    hook_path = path.expanduser('~/.sweep/hooks/' + name)
    if path.exists(hook_path):
        # run the script with the given args
        click.secho('Found hook for {}, running {}'.format(name, hook_path), fg='blue')
        check_call([hook_path] + list(args))
