#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'requests',
    'prompt_toolkit',
    'pygments',
    'terminaltables',
]

setup_requirements = [
    'pytest-runner',
    # TODO(dropseedlabs): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='sweep',
    version='0.4.4',
    description="A simple CLI for responding to and merging pull requests.",
    long_description=readme + '\n\n' + history,
    author="Dropseed, LLC",
    author_email='python@dropseed.io',
    url='https://github.com/dropseedlabs/sweep',
    packages=find_packages(include=['sweep']),
    entry_points={
        'console_scripts': [
            'sweep=sweep.cli:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='sweep',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
