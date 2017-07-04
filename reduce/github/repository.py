import click
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter

from .api import graphql
from .pull_request import PullRequest
from ..prompt_validators import ChoiceValidator


class Repository(object):
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name
        self.full_name = '{}/{}'.format(self.owner.name, self.name)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_open_pull_requests(self):
        query = """query {
                    repository(owner: "%s", name: "%s") {
                      pullRequests(first: 100, states: OPEN) {
                        edges {
                          node {
                            number
                            title
                          }
                        }
                      }
                    }
                }""" % (self.owner.name, self.name)

        # TODO add paging
        query_data = graphql(query)
        pulls = [x['node'] for x in query_data['repository']['pullRequests']['edges']]
        return pulls

    def command_prompt(self):
        pr_number_input = None
        while pr_number_input != 'done':
            click.secho('Getting open pull requests for {}...'.format(self.full_name), fg='yellow')
            pulls = self.get_open_pull_requests()

            if not pulls:
                click.secho('There are no repos with open pull requests!', fg='green')
                return

            # print the repo name and list of open prs
            click.clear()
            click.secho(self.full_name, bold=True)
            click.secho('\nThere are {} open pull requests:\n'.format(len(pulls)))
            for pull in pulls:
                click.secho('#{} - {}'.format(pull['number'], pull['title']))

            click.secho('\nEnter a PR number or hit enter to work through them in order.')
            pr_numbers = [str(x['number']) for x in pulls] + ['done']
            pr_number_input = prompt(
                u'> ',
                completer=WordCompleter(pr_numbers),
                validator=ChoiceValidator(pr_numbers, allow_empty=True),
            )

            if pr_number_input == 'done':
                pass
            elif pr_number_input == '':
                for pr in pulls:
                    pull = PullRequest(repo=self, number=pr['number'])
                    pull.print_overview()
                    pull.command_prompt()

                # exit the while loop by returning when done
                return
            else:
                click.secho('Getting {} #{}...'.format(self, pr_number_input), fg='yellow')
                pull = PullRequest(repo=self, number=pr_number_input)
                pull.print_overview()
                pull.command_prompt()
