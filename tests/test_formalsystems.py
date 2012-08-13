#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import doctest

import os
import sys

# Managing path
DIRNAME = os.path.abspath(os.path.dirname(__file__))
UP_DIR  = os.path.dirname(DIRNAME)

if UP_DIR not in sys.path:
    sys.path.append(UP_DIR)

# Now we can import the tested packages/modules
from formalsystems import formalsystems, leplparsing


class TestFormalSystems(unittest.TestCase):

    def setUp(self):
        pass



if __name__ == '__main__':

    # Going in tests directory
    os.chdir(DIRNAME)

    flags = (
        doctest.ELLIPSIS |
        doctest.NORMALIZE_WHITESPACE
    )
    # Would run only local unit tests
    #unittest.main()

    tests = unittest.TestSuite()

    tests.addTests(unittest.makeSuite(TestFormalSystems))
    tests.addTests(doctest.DocTestSuite(formalsystems))
    tests.addTests(doctest.DocTestSuite(leplparsing))
    tests.addTests(doctest.DocFileSuite('../README.rst', module_relative=False, optionflags=flags)) 

    # Test runner
    verbosity = 0

    if len(sys.argv) >= 2:

        first_arg = sys.argv[1].strip()

        if first_arg == '-vv':
            verbosity = 2

        elif first_arg == '-v':
            verbosity = 1

    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(tests)

