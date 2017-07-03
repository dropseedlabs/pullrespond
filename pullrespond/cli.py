# -*- coding: utf-8 -*-

"""Console script for pullrespond."""

import click

from .pullrespond import graphql_query


@click.command()
@click.argument('organization')
def main(organization):
    """Console script for pullrespond."""
    # query = """query {
    #           viewer {
    #             organizations(first: 20) {
    #               edges {
    #                 node {
    #                   name
    #                   login
    #                 }
    #               }
    #             }
    #           }
    #         }"""
    # data = graphql_query(query)
    # orgs = [x['node'] for x in data['viewer']['organizations']['edges']]
    #
    # click.secho('You have access to the following GitHub orgs:')
    # click.secho('---------------------------------------------')
    # for index, org in enumerate(orgs):
    #     click.secho('[{}] {}'.format(index, org['name']))
    #
    # org_index = click.prompt('Which one do you want to work on?', type=int)
    #
    # org = orgs[org_index]
    # org_login = org['login']

    click.secho('Getting open pull requests for {}...'.format(organization), fg='yellow')

    query = """query {
              organization(login: "%s") {
                repositories(first: 100) {
                  edges {
                    node {
                      name
                      pullRequests(first: 100, states: OPEN) {
                        edges {
                          node {
                            state
                            number
                            title
                            body
                          }
                        }
                      }
                    }
                  }
                }
              }
            }""" % organization

    pulls_query_data = graphql_query(query)
    repos = [x['node'] for x in pulls_query_data['organization']['repositories']['edges']]

    for repo in repos:
        pulls = [x['node'] for x in repo['pullRequests']['edges']]
        if pulls:
            repo_name = repo['name']
            click.secho('Working on pull requests for {}'.format(repo_name))
            click.secho('There are {} currently open'.format(len(pulls)))

            for pull in pulls:


    # first get token
    # - choose an org
    # - all repos (or with substring)
    # - all prs (or prs with label, substring)
    #
    # for each pr
    # show title, statuses
    # merge, skip, comment


if __name__ == "__main__":
    main()
