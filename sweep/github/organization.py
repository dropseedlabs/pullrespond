import click
from terminaltables import AsciiTable

from .api import graphql
from .repository import Repository
from ..object_prompt import ObjectPrompt


class Organization(ObjectPrompt):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(Organization, self).__init__(
            commands=[],
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
