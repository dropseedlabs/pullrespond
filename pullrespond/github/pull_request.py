import urllib

import requests
import click
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import TerminalFormatter

from .api import graphql, rest
from ..prompt_validators import ChoiceValidator


PROMPT_COMMANDS = [
    'merge',
    'done',
    # 'commits',
    # 'comments',
    'comment',
    'overview',
    'diff',
    # 'open',
    # 'review',
    # 'reviews',
]


class PullRequest(object):
    def __init__(self, repo, number):
        self.repo = repo
        self.number = int(number)

    def __unicode__(self):
        return u'{}#{}'.format(self.repo, self.number)

    def __str__(self):
        return '{}#{}'.format(self.repo, self.number)

    def command_prompt(self):
        command_input = None
        while command_input not in ('done', ''):
            command_input = prompt(
                u'> ',
                completer=WordCompleter(PROMPT_COMMANDS),
                validator=ChoiceValidator(PROMPT_COMMANDS, allow_empty=True),
            )
            if command_input == 'overview':
                self.print_overview()
            elif command_input == 'merge':
                self.merge_prompt()
            elif command_input == 'comment':
                self.comment_prompt()
                click.secho('Comment created.', fg='green')
            elif command_input == 'diff':
                self.print_diff()

    def comment_prompt(self):
        # could complete usernames with @...
        click.secho('Enter comment (press ESC then ENTER to finish)')
        comment = prompt(
            u'--> ',
            mouse_support=True,
            multiline=True,
        )
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      pullRequest(number: %s) {
                        id
                      }
                    }
                }""" % (self.repo.owner.name, self.repo.name, self.number)
        pull_request_id = graphql(query)['repository']['pullRequest']['id']
        mutation = """mutation {
                        addComment(input:{subjectId: "%s", body: "%s"}) {
                          clientMutationId
                        }
                      }""" % (pull_request_id, comment)
        graphql(mutation)

    def merge_prompt(self):
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      pullRequest(number: %s) {
                        title
                        headRefName
                        commits(last: 1) {
                          edges {
                            node {
                              commit {
                                oid
                              }
                            }
                          }
                        }
                      }
                    }
                }""" % (self.repo.owner.name, self.repo.name, self.number)
        pull_data = graphql(query)['repository']['pullRequest']
        pull_title = pull_data['title']
        sha = pull_data['commits']['edges'][0]['node']['commit']['oid']

        # can't seem to merge with graphql yet
        endpoint = '/repos/{}/pulls/{}/merge'.format(self.repo.full_name, self.number)
        data = {
            'commit_title': '{} (#{})'.format(pull_title, self.number),
            'commit_message': '',
            'sha': sha,
            'merge_method': 'squash',
        }
        rest(requests.put, endpoint, data)

        click.secho('PR successfully merged.', fg='green')

        branch_name = pull_data['headRefName']
        if click.confirm('Delete the {} branch?'.format(branch_name)):
            endpoint = '/repos/{}/git/refs/heads/{}'.format(self.repo.full_name, urllib.quote_plus(branch_name))
            rest(requests.delete, endpoint)
            click.secho('{} deleted.'.format(branch_name), fg='green')

    def print_overview(self):
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      pullRequest(number: %s) {
                        id
                        number
                        title
                        bodyText
                        baseRefName
                        headRefName
                        author {
                          login
                        }
                        createdAt
                        mergeable
                        url
                        comments {
                          totalCount
                        }
                        reviews {
                          totalCount
                        }
                        reviewRequests {
                          totalCount
                        }
                        state
                        commits(last: 1) {
                          totalCount
                          edges {
                              node {
                                commit {
                                  status {
                                    id
                                    state
                                    contexts {
                                      context
                                      description
                                      state
                                      targetUrl
                                    }
                                  }
                                }
                              }
                            }
                          }
                      }
                    }
                }""" % (self.repo.owner.name, self.repo.name, self.number)

        query_data = graphql(query)
        overview = query_data['repository']['pullRequest']

        click.clear()
        click.secho(self.repo.full_name)
        click.secho('#{} {} - {}'.format(overview['number'], overview['state'], overview['title']), bold=True)
        click.secho('{author} wants to merge {commits} commit from {head} into {base}'.format(
                author=overview['author']['login'],
                commits=overview['commits']['totalCount'],
                head=overview['headRefName'],
                base=overview['baseRefName'],
            )
        )

        click.secho('Comments: {}'.format(overview['comments']['totalCount']))
        click.secho('Reviews: {}'.format(overview['reviews']['totalCount']))
        click.secho('Review requests: {}'.format(overview['reviewRequests']['totalCount']))

        if overview['mergeable']:
            click.echo('Mergeable: ' + click.style(u'\u2714', fg='green'))
        else:
            click.echo('Mergeable: ' + click.style(u'\u2718', fg='red'))

        last_commit_status = overview['commits']['edges'][0]['node']['commit']['status']

        if last_commit_status:
            def color_for_state(state):
                if state == 'PENDING':
                    return 'yellow'
                if state == 'SUCCESS':
                    return 'green'
                if state == 'FAILURE':
                    return 'red'

            click.echo('Status: ' + click.style(last_commit_status['state'], fg=color_for_state(last_commit_status['state'])))
            for context in last_commit_status['contexts']:
                click.secho('- {context}: {description}'.format(
                    context=context['context'],
                    description=context['description'],
                ), fg=color_for_state(context['state']))

        # click.secho('\nBody:')
        # click.secho(overview['bodyText'])

    def print_diff(self):
        endpoint = '/repos/{}/pulls/{}'.format(self.repo.full_name, self.number)
        diff = rest(requests.get, endpoint, headers={'Accept': 'application/vnd.github.v3.diff'})
        highlighted = highlight(diff, DiffLexer(), TerminalFormatter())
        click.echo_via_pager(highlighted)
