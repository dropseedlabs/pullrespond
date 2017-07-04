import os
import click
import requests


def get_github_token():
    token_file_path = os.path.expanduser('~/.reduce/github_token')
    if not os.path.exists(token_file_path):
        click.secho('We didn\'t find a GitHub API token in {}.'.format(token_file_path))
        click.secho('Please go to https://github.com/settings/tokens and generate a new token with these permissions:')
        click.secho('- repo\n- read:org')
        click.secho('')
        token = click.prompt('Enter the token and we\'ll save it to {}'.format(token_file_path))

        os.makedirs(os.path.dirname(token_file_path))  # probably don't have ~/.reduce yet
        with open(token_file_path, 'w+') as f:
            f.write(token)

    with open(token_file_path, 'r') as f:
        token = f.read().strip()

    return token


def get_headers():
    token = get_github_token()
    headers = {'Authorization': 'token {}'.format(token)}
    return headers


def graphql(query):
    response = requests.post(
        'https://api.github.com/graphql',
        headers=get_headers(),
        json={'query': query}
    )

    response.raise_for_status()

    data = response.json()['data']

    if data == None:
        raise Exception('No data in response.\n{}'.format(response.text))

    return data


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
