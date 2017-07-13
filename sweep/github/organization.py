import re

import click
from terminaltables import AsciiTable

from .api import graphql, GraphqlErrorsException
from .repository import Repository
from .pull_request import PullRequest
from ..object_prompt import ObjectPrompt


class Organization(ObjectPrompt):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(Organization, self).__init__(
            child_key='name',
            pre_prompt_message='Enter a repo name or command (TAB for options).',
            *args,
            **kwargs
        )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_children(self):
        click.secho('Getting {} repos...'.format(self), fg='yellow')
        query = """query {
                  organization(login: "%s") {
                    repositories(first: 100, after: null) {
                      pageInfo {
                        endCursor
                        hasNextPage
                      }
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

        repo_nodes = graphql(query, to_return_path='organization.repositories.edges', page_info_path='organization.repositories.pageInfo')
        repos = [x['node'] for x in repo_nodes]
        return repos

    def repos_with_pulls(self):
        if not self.children:
            self.children = self.get_children()

        return [x for x in self.children if x['pullRequests']['totalCount']]

    def get_child_object_prompt(self, key):
        return Repository(owner=self, name=key)

    def overview(self, refresh=True):
        if refresh:
            self.children = self.get_children()

        click.clear()

        repos = self.repos_with_pulls()

        table_data = [
            ['Repos ({})'.format(len(repos)), 'Pull requests ({})'.format(sum([repo['pullRequests']['totalCount'] for repo in repos]))],
        ]
        for repo in repos:
            table_data.append([
                repo['name'],
                '{} open'.format(repo['pullRequests']['totalCount']),
            ])
        table = AsciiTable(table_data)
        click.echo(table.table)

    def filter_pulls(self, state, title):
        pulls = []

        for repo in self.repos_with_pulls():
            query = """query {
                        repository(owner: "%s", name: "%s") {
                          pullRequests(states: %s, first: 100, after: null) {
                            totalCount
                            pageInfo {
                              endCursor
                              hasNextPage
                            }
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
                    }""" % (self.name, repo['name'], state.upper())

            pull_nodes = graphql(query, to_return_path='repository.pullRequests.edges', page_info_path='repository.pullRequests.pageInfo')
            repo_pulls = [x['node'] for x in pull_nodes]
            pulls += repo_pulls

        if title:
            pulls = [x for x in pulls if re.search(title, x['title'])]

        return pulls
