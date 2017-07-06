import click
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from terminaltables import AsciiTable

from .api import graphql
from .repository import Repository
from ..prompt_validators import ChoiceValidator


class Organization(object):
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_repos(self):
        query = """query {
                  organization(login: "%s") {
                    repositories(first: 100) {
                      edges {
                        node {
                          name
                          pullRequests(states: OPEN) {
                            totalCount
                          }
                        }
                      }
                    }
                  }
                }""" % self.name

        # TODO add paging
        query_data = graphql(query)
        repos = [x['node'] for x in query_data['organization']['repositories']['edges']]
        return repos

    def command_prompt(self):
        repo_input = None
        while repo_input != 'done':
            click.secho('Getting open pull requests for {}...'.format(self), fg='yellow')
            repos = self.get_repos()
            with_open_pulls = [x for x in repos if x['pullRequests']['totalCount']]

            if not with_open_pulls:
                click.secho('There are no repos with open pull requests!', fg='green')
                return

            click.clear()

            table_data = [
                ['Repos ({})'.format(len(with_open_pulls)), 'Pull requests ({})'.format(sum([repo['pullRequests']['totalCount'] for repo in with_open_pulls]))],
            ]
            for repo in with_open_pulls:
                table_data.append([
                    repo['name'],
                    '{} open'.format(repo['pullRequests']['totalCount']),
                ])
            table = AsciiTable(table_data)
            click.echo(table.table)

            click.secho('\nEnter a repo name or hit enter to work through them in order.')
            repo_names = [x['name'] for x in with_open_pulls] + ['done']
            repo_input = prompt(
                u'Repo > ',
                completer=WordCompleter(repo_names),
                validator=ChoiceValidator(repo_names, allow_empty=True),
            )

            if repo_input == 'done':
                pass
            elif repo_input == '':
                for r in with_open_pulls:
                    repo = Repository(owner=self, name=r['name'])
                    repo.command_prompt()
                # exit the while loop by returning when done
                return
            else:
                repo = Repository(owner=self, name=repo_input)
                repo.command_prompt()
