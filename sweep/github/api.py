import re
from copy import deepcopy
import os
import click
import requests


class GraphqlErrorsException(Exception):
    pass


def get_github_token():
    token_file_path = os.path.expanduser('~/.sweep/github_token')
    if not os.path.exists(token_file_path):
        click.secho('We didn\'t find a GitHub API token in {}.'.format(token_file_path))
        click.secho('Please go to https://github.com/settings/tokens and generate a new token with these permissions:')
        click.secho('- repo\n- read:org')
        click.secho('')
        token = click.prompt('Enter the token and we\'ll save it to {}'.format(token_file_path))

        os.makedirs(os.path.dirname(token_file_path))  # probably don't have ~/.sweep yet
        with open(token_file_path, 'w+') as f:
            f.write(token)

    with open(token_file_path, 'r') as f:
        token = f.read().strip()

    return token


def get_headers():
    token = get_github_token()
    headers = {'Authorization': 'token {}'.format(token)}
    return headers


def graphql(query, to_return_path=None, page_info_path=None, after=None):
    if after:
        query = re.sub('after: .*\)', 'after: "{}")'.format(after), query)

    response = requests.post(
        'https://api.github.com/graphql',
        headers=get_headers(),
        json={'query': query}
    )

    response.raise_for_status()

    errors = response.json().get('errors', None)
    if errors:
        raise GraphqlErrorsException(errors)

    data = response.json()['data']
    if data == None:
        raise Exception('No data in response.\n{}'.format(response.text))

    data_to_return = deepcopy(data)

    if to_return_path:
        for p in to_return_path.split('.'):
            data_to_return = data_to_return[p]

    if page_info_path:
        # we'll are going to assume there's only 1 paginated object
        # and it's in the top 2 levels
        page_info = deepcopy(data)
        for p in page_info_path.split('.'):
            page_info = page_info[p]

        if 'endCursor' not in page_info:
            raise Exception('pageInfo not found, but we didn\'t try very hard.')

        if page_info['hasNextPage']:
            next_data = graphql(query, to_return_path=to_return_path, page_info_path=page_info_path, after=page_info['endCursor'])
            data_to_return = data_to_return + next_data

    return data_to_return


def rest(requests_func, endpoint, data=None, headers={}):
    request_headers = get_headers()
    request_headers.update(headers)

    response = requests_func(
        'https://api.github.com' + endpoint,
        headers=request_headers,
        json=data,
    )

    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        return response.text
