#-*- coding: utf-8 -*-
"""
Test runner

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import os
import sys

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..")))

import unittest

from ast.test_automaton import TestNFA, TestDFA
from ast.test_lexer import TestLexer
from ast.test_parser import TestParser
from compile.test_compiler import TestCompiler


def load():
    return (
        TestNFA.load_cases(),
        TestDFA.load_cases(),
        TestLexer.load_cases(),
        TestParser.load_cases(),
        TestCompiler.load_cases())


def run():
    ts = unittest.TestSuite()
    for suite in load():
        ts.addTests(suite)

    tr = unittest.TextTestRunner()
    ret = tr.run(ts)
    return ret.wasSuccessful()


if __name__ == "__main__":
    if run():
        exit(0)
    else:
        exit(1)
