#!/usr/bin/env python

from setuptools import setup

setup(
    name='geppetto',
    version='0.0.1',
    description='Figaro, look! He\'s alive! He can talk!',
    author='Kristoffer Nilsson',
    author_email='smrt@novafaen.se',
    url='http://smrt.novafaen.se/',
    packages=['geppetto'],
    requires=[
        'smrt',
        'schedule',
        'requests',
        'pysolar',
        'pytz'
    ],
    dependency_links=[
        'git+https://github.com/novafaen/smrt.git'
    ],
    test_suite='tests',
    tests_require=[

    ])
