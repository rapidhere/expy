# -*- coding: utf-8 -*
"""
Automaton cases

Author: rapidhere@gmail.com
"""

import unittest
import yaml
import os

from expy.ast.automaton import NFA, DFA


class TestNFA(unittest.TestCase):
    def __init__(self, description, regex, result):
        unittest.TestCase.__init__(self, "test_parse")

        self.description = description
        self.regex = regex
        self.result = sorted(result)

    def test_parse(self):
        nfa = NFA(self.regex).parse()
        self.assertListEqual(sorted(nfa.dump()), self.result)

    @classmethod
    def load_cases(cls):
        cases = load_yaml("nfa_cases.yaml")
        for case in cases:
            for i in xrange(0, len(case["result"])):
                case["result"][i] = tuple(case["result"][i])

        return [cls(**case) for case in cases]


class TestDFA(unittest.TestCase):
    def __init__(self, test_method, input, colored_dfa):
        unittest.TestCase.__init__(self, test_method)

        self.input = input
        self.colored_dfa = colored_dfa

    def test_color(self):
        nfa = self.load_nfa()
        dfa = DFA(nfa)
        dfa.__DFA__color()
        self.assertListEqual(sorted(dfa.dump()), sorted(self.colored_dfa))

    def load_nfa(self):
        return

    @classmethod
    def load_cases(cls):
        pass


def load_yaml(file_name):
    with file(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return [x for x in yaml.load_all(f.read())][0]
