# -*- coding: utf-8 -*-

"""Main module."""

import click
import requests


GRAPHQL_URL = 'https://api.github.com/graphql'


def graphql_query(query):
    token = ''
    headers = {'Authorization': 'token {}'.format(token)}

    response = requests.post(GRAPHQL_URL, headers=headers, json={'query': query})

    if response.status_code != 200:
        click.secho('GraphQL request failed.', fg='red')
        exit(1)

    return response.json()['data']
