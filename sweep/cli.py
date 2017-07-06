# -*- coding: utf-8 -*-

"""Console script for sweep."""

import click

from .github import Organization


@click.command()
@click.argument('organization')
def main(organization):
    """Interactively work through an organization's pull requests"""

    organization = Organization(organization)
    organization.command_prompt()
    click.secho('Done!', fg='green')


if __name__ == "__main__":
    main()
