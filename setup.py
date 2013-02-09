#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='FormalSystems',
    version='0.1.2',
    description='Play with formal systems from "Gödel Escher Bach", Douglas Hofstadter',
    author='Alex Prengère',
    author_email='alexprengere@gmail.com',
    url='http://alexprengere.github.com/FormalSystems',
    packages=[
        'formalsystems', 
    ],
    py_modules=[
        'FormalSystemsMain' 
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
    #package_data={'formalsystems': ['example_definitions/*.yaml']},
    #package_dir={'mypkg': 'src/mypkg'},
    #data_files=[
    #    ('/etc/init.d', ['init-script'])
    #]
)
