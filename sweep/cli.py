# -*- coding: utf-8 -*-

"""Console script for sweep."""

import click

from .github import Organization, Repository, PullRequest
from .github.pull_request import print_pulls_table


@click.group(invoke_without_command=True)
@click.argument('organization')
@click.pass_context
def organization(ctx, organization):
    """Interactively work through an organization's pull requests"""

    organization = Organization(organization)
    ctx.obj['organization'] = organization

    if ctx.invoked_subcommand is None:
        organization.command_prompt(ctx, default_subcommand='repo')
        click.secho('Done!', fg='green')
    # else:
    #     click.echo('I am about to invoke %s' % ctx.invoked_subcommand)


@organization.command('overview')
@click.pass_context
def organization_overview(ctx):
    """Organization overview"""
    organization = ctx.obj['organization']
    organization.overview()


@organization.group(invoke_without_command=True)
@click.option('--state', default='open', help='Filter by PR state')
@click.option('--title', default=None, help='Filter by PR title')
@click.option(
    '--status',
    default=None,
    help='Filter by PR latest commit status',
    type=click.Choice(['PENDING', 'SUCCESS', 'FAILURE'])
)
@click.pass_context
def pulls(ctx, state, title, status):
    """View or modify pull requests"""

    organization = ctx.obj['organization']
    pulls = organization.filter_pulls(state=state, title=title, status=status)
    ctx.obj['pulls'] = pulls

    if ctx.invoked_subcommand is None:
        print_pulls_table(pulls)


# TODO add merge mode
@pulls.command('merge')
@click.pass_context
def merge_pulls(ctx):
    """Merge pull requests"""
    organization = ctx.obj['organization']
    pulls = ctx.obj['pulls']
    print_pulls_table(pulls)

    # will_delete = 'The branches will be deleted too.' if delete_branch else 'The branches will NOT be deleted.'
    if click.confirm(click.style('Are you sure you want to merge these pull requests?', fg='red')):
        if click.confirm(click.style('Are you positive!?', fg='red')):
            for pull in pulls:
                ctx.obj['repository'] = Repository(owner=organization, name=pull['repository']['name'])
                ctx.obj['pull'] = PullRequest(repo=ctx.obj['repository'], number=pull['number'])
                try:
                    ctx.invoke(merge)
                except Exception:
                    click.secho('Failed to merge {}'.format(pull), fg='red')
                    click.confirm('Continue with the rest?', abort=True)


@pulls.command('close')
@click.pass_context
def close_pulls(ctx):
    """Close pull requests"""
    organization = ctx.obj['organization']
    pulls = ctx.obj['pulls']
    print_pulls_table(pulls)

    if click.confirm(click.style('Are you sure you want to close these pull requests?', fg='red')):
        if click.confirm(click.style('Are you positive!?', fg='red')):
            for pull in pulls:
                ctx.obj['repository'] = Repository(owner=organization, name=pull['repository']['name'])
                ctx.obj['pull'] = PullRequest(repo=ctx.obj['repository'], number=pull['number'])
                try:
                    ctx.invoke(close)
                except Exception:
                    click.secho('Failed to close {}'.format(pull), fg='red')
                    click.confirm('Continue with the rest?', abort=True)


@organization.group('labels')
@click.pass_context
def organization_labels(ctx):
    pass


@organization_labels.command('create')
@click.argument('name')
@click.argument('color')
@click.pass_context
def create_label_on_organization_repos(ctx, *args, **kwargs):
    organization = ctx.obj['organization']
    for repo in organization.get_children():
        ctx.obj['repository'] = Repository(owner=organization, name=repo['name'])
        ctx.invoke(create_repo_label, *args, **kwargs)


@organization.group(invoke_without_command=True)
@click.argument('name')
@click.pass_context
def repo(ctx, name):
    """View or modify a repo"""
    organization = ctx.obj['organization']
    repo = Repository(owner=organization, name=name)
    ctx.obj['repository'] = repo

    if ctx.invoked_subcommand is None:
        repo.command_prompt(ctx, default_subcommand='pull')


@repo.command('overview')
@click.pass_context
def repo_overview(ctx):
    """Repo overview"""
    repo = ctx.obj['repository']
    repo.overview()


@repo.command('open')
@click.pass_context
def repo_open(ctx):
    """Open repo is browser"""
    repo = ctx.obj['repository']
    repo.open()


@repo.group(invoke_without_command=True)
@click.argument('number', type=int)
@click.pass_context
def pull(ctx, number):
    """View or modify pull request"""
    repo = ctx.obj['repository']
    pull = PullRequest(repo=repo, number=number)
    ctx.obj['pull'] = pull

    if ctx.invoked_subcommand is None:
        pull.command_prompt(ctx)


@repo.group('labels')
@click.pass_context
def repo_labels(ctx):
    pass


@repo_labels.command('create')
@click.argument('name')
@click.argument('color')
@click.pass_context
def create_repo_label(ctx, name, color):
    repo = ctx.obj['repository']
    repo.create_label(name, color)


@pull.command('overview')
@click.pass_context
def pull_overview(ctx):
    """Pull request overview"""
    pull = ctx.obj['pull']
    pull.overview()


@pull.command()
@click.option('--delete-branch', default=True)
@click.pass_context
def merge(ctx, delete_branch):
    """Merge pull request"""
    pull = ctx.obj['pull']
    pull.merge(delete_branch)


@pull.command()
@click.option('--delete-branch', default=True)
@click.pass_context
def close(ctx, delete_branch):
    """Close pull request"""
    pull = ctx.obj['pull']
    pull.close(delete_branch)


@pull.command()
@click.pass_context
def files_changed(ctx):
    """View list of PR files changed"""
    pull = ctx.obj['pull']
    pull.files_changed()


@pull.command()
@click.pass_context
def open(ctx):
    """Open PR in browser"""
    pull = ctx.obj['pull']
    pull.open()


@pull.command()
@click.pass_context
def diff(ctx):
    """View git diff of PR"""
    pull = ctx.obj['pull']
    pull.diff()


@pull.command()
@click.pass_context
def review(ctx):
    """Add a PR review"""
    pull = ctx.obj['pull']
    pull.review()

    click.secho('Review added.'.format(review), fg='green')


@pull.command()
@click.pass_context
def comment(ctx):
    """Add a PR comment"""
    pull = ctx.obj['pull']
    pull.comment()

    click.secho('Comment created.', fg='green')


cli = organization(obj={})


if __name__ == "__main__":
    cli()
