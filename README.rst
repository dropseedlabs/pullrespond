===========
sweep
===========


.. image:: https://travis-ci.org/dropseedlabs/sweep.svg?branch=master
        :target: https://travis-ci.org/dropseedlabs/sweep

.. image:: https://img.shields.io/pypi/v/sweep.svg
        :target: https://pypi.python.org/pypi/sweep

.. image:: https://img.shields.io/pypi/l/sweep.svg
        :target: https://pypi.python.org/pypi/sweep

.. image:: https://img.shields.io/pypi/pyversions/sweep.svg
        :target: https://pypi.python.org/pypi/sweep



A CLI for responding to and merging pull requests.


Installation
------------

.. code-block:: bash

    pip install sweep

Usage
-----

.. code-block:: bash

    sweep <organization slug>

Hooks
-----

There are several places where a user can run a custom script as a part of their
process (i.e. deploying after a merge). Put an executable script matching the
name of the hook at ``~/.sweep/hooks/<hook_name>``. Each hook will also
receive a set of arguments, which you can use in your script.

* ``post_merge`` - runs right after a successful merge

  - repo name
  - PR number
  - repo full name (owner/repo)
