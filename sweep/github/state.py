import click


def styled_state(state, colored=True, short=True):
    if not state:
        return ''

    color = None
    string = state

    if colored:
        color = color_for_state(state)

    if short:
        if state == 'PENDING':
            string = '?'
        if state == 'SUCCESS':
            string = u'\u2714'
        if state == 'FAILURE':
            string = u'\u2718'

    return click.style(string, fg=color)


def color_for_state(state):
    if state == 'PENDING':
        return 'yellow'
    if state == 'SUCCESS':
        return 'green'
    if state == 'FAILURE':
        return 'red'

    return None
