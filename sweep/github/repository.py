import webbrowser
import click
from terminaltables import AsciiTable

from .api import graphql
from .pull_request import PullRequest
from ..object_prompt import ObjectPrompt
from .state import styled_state


class Repository(ObjectPrompt):
    def __init__(self, owner, name, *args, **kwargs):
        self.owner = owner
        self.name = name
        self.full_name = '{}/{}'.format(self.owner.name, self.name)
        super(Repository, self).__init__(
            child_key='number',
            pre_prompt_message='Enter a PR number or hit enter to work through them in order.',
            *args,
            **kwargs
        )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_children(self):
        click.secho('Getting open pull requests for {}...'.format(self.full_name), fg='yellow')
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      pullRequests(first: 100, states: OPEN) {
                        edges {
                          node {
                            number
                            title
                            author { login }
                            commits(last: 1) {
                              edges {
                                node {
                                  commit {
                                    status {
                                      state
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                }""" % (self.owner.name, self.name)

        # TODO add paging
        query_data = graphql(query)
        pulls = [x['node'] for x in query_data['repository']['pullRequests']['edges']]
        return pulls

    def get_child_object_prompt(self, key):
        return PullRequest(repo=self, number=key)

    def overview(self, refresh=True):
        # print the repo name and list of open prs
        if refresh:
            self.children = self.get_children()

        click.clear()
        click.secho(self.full_name, bold=True)
        click.secho('\nThere are {} open pull requests:\n'.format(len(self.children)))

        table_data = [
            ['Number', 'Status', 'Author', 'Title'],
        ]
        for pull in self.children:
            status = pull['commits']['edges'][0]['node']['commit']['status']
            status = styled_state(status['state']) if status else ''
            table_data.append([
                pull['number'],
                status,
                pull['author']['login'],
                pull['title'],
            ])
        table = AsciiTable(table_data)
        click.echo(table.table)

    def open(self):
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      url
                    }
                }""" % (self.owner.name, self.name)
        url = graphql(query)['repository']['url']
        click.secho('Opening {} in your browser...'.format(url), fg='yellow')
        webbrowser.open(url)
