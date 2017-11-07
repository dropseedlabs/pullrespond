import webbrowser
import click
from terminaltables import AsciiTable
import requests

from .api import graphql, rest
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
            pre_prompt_message='Enter a PR number or command (TAB for options).',
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
                      pullRequests(first: 100, states: OPEN, after: null) {
                        pageInfo {
                          endCursor
                          hasNextPage
                        }
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

        pull_nodes = graphql(query, to_return_path='repository.pullRequests.edges', page_info_path='repository.pullRequests.pageInfo')
        pulls = [x['node'] for x in pull_nodes]
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

    def create_label(self, name, color):
        if color.startswith('#'):
            color  = color[1:]

        data = {'name': name, 'color': color}
        click.secho('Adding "{}" label to {}'.format(name, self.full_name))

        try:
            rest(requests.post, '/repos/{}/{}/labels'.format(self.owner.name, self.name), data=data)
        except requests.exceptions.HTTPError as e:
            response = e.response
            if response.json().get('errors', []):
                for error in response.json()['errors']:
                    click.secho('Field "{}" {}'.format(error['field'], error['code']), fg='red')
            else:
                raise e
