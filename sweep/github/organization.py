import click
from terminaltables import AsciiTable

from .api import graphql
from .repository import Repository
from .pull_request import PullRequest
from ..object_prompt import ObjectPrompt


class Organization(ObjectPrompt):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(Organization, self).__init__(
            commands=[
                'bulk_squash_merge_delete_by_title',
            ],
            child_key='name',
            pre_prompt_message='Enter a repo name or hit enter to work through them in order.',
            *args,
            **kwargs
        )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_children(self):
        click.secho('Getting open pull requests for {}...'.format(self), fg='yellow')
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
        return [x for x in repos if x['pullRequests']['totalCount']]

    def get_child_object_prompt(self, key):
        return Repository(owner=self, name=key)

    def overview(self, refresh=True):
        if refresh:
            self.children = self.get_children()

        click.clear()

        table_data = [
            ['Repos ({})'.format(len(self.children)), 'Pull requests ({})'.format(sum([repo['pullRequests']['totalCount'] for repo in self.children]))],
        ]
        for repo in self.children:
            table_data.append([
                repo['name'],
                '{} open'.format(repo['pullRequests']['totalCount']),
            ])
        table = AsciiTable(table_data)
        click.echo(table.table)

    def bulk_squash_merge_delete_by_title(self, *args):
        if len(args) != 1 or args[0].strip() == '':
            click.secho('Wrong number of args. You should put 1 string wrapped in quotes after the command.', fg='red')
            return

        title_search = args[0].strip('"\'')

        query = """query {
                  organization(login: "%s") {
                    repositories(first: 100) {
                      edges {
                        node {
                          pullRequests(states: OPEN, first: 100) {
                            totalCount
                            edges {
                             node {
                               title
                               number
                               author {
                                 login
                               }
                               repository { name }
                             }
                            }
                          }
                        }
                      }
                    }
                  }
                }""" % self.name

        # TODO add paging
        query_data = graphql(query)
        repos = [x['node'] for x in query_data['organization']['repositories']['edges']]
        with_open_pulls = [x for x in repos if x['pullRequests']['totalCount']]

        table_data = [
            ['Repo', 'Number', 'Author', 'Title']
        ]

        matching_pulls = []

        for repo in with_open_pulls:
            for pull_edge in repo['pullRequests']['edges']:
                if title_search in pull_edge['node']['title']:
                    pull_edge['repo'] = repo
                    matching_pulls.append(pull_edge['node'])

        for pull in matching_pulls:
            table_data.append([
                pull['repository']['name'],
                pull['number'],
                pull['author']['login'],
                pull['title'],
            ])

        table = AsciiTable(table_data)
        click.secho('The following pull requests match your search.', fg='green')
        click.echo(table.table)

        if matching_pulls and click.confirm('Do you want to squash merge these pull requests and delete the branches?'):
            for pull in matching_pulls:
                pr = PullRequest(repo=Repository(owner=self, name=pull['repository']['name']), number=pull['number'])
                click.secho(str(pr), fg='blue')

            # just make it wait before cleaing the screen
            click.prompt('Done! Hit any key to continue')
