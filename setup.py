#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

from setuptools import setup


with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name='FormalSystems',
    version='0.1.3',
    author='Alex Prengère',
    author_email='alexprengere@gmail.com',
    url='http://alexprengere.github.com/FormalSystems',
    description='Play with formal systems from "Gödel Escher Bach", Douglas Hofstadter',
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    packages=[
        'formalsystems',
    ],
    py_modules=[
        'FormalSystemsMain',
    ],
    install_requires=[
        'lepl',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'FormalSystems = FormalSystemsMain:main',
        ]
    },
    # We do not export YAML definitions with sources when installing
    # package_data={'formalsystems': ['example_definitions/*.yaml']},
    # package_dir={'mypkg': 'src/mypkg'},
    # data_files=[
    #     ('/etc/init.d', ['init-script'])
    # ]
)
