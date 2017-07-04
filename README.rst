===========
reduce
===========


.. image:: https://travis-ci.org/dropseedlabs/reduce.svg?branch=master
        :target: https://travis-ci.org/dropseedlabs/reduce

.. image:: https://img.shields.io/pypi/v/reduce.svg
        :target: https://pypi.python.org/pypi/reduce

.. image:: https://img.shields.io/pypi/l/reduce.svg
        :target: https://pypi.python.org/pypi/reduce

.. image:: https://img.shields.io/pypi/pyversions/reduce.svg
        :target: https://pypi.python.org/pypi/reduce



A CLI for responding to and merging pull requests.


Installation
------------

.. code-block:: bash

    pip install reduce

Usage
-----

.. code-block:: bash

    reduce <organization slug>

Hooks
-----

There are several places where a user can run a custom script as a part of their
process (i.e. deploying after a merge). Put an executable script matching the
name of the hook at ``~/.reduce/hooks/<hook_name>``. Each hook will also
receive a set of arguments, which you can use in your script.

* ``post_merge`` - runs right after a successful merge

  - repo name
  - PR number
  - repo full name (owner/repo)
