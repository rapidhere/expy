# -*- coding: utf-8 -*
"""
Automaton cases

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import unittest
import yaml
import os

from expy.ast.automaton import NFA, DFA, AutomatonNode


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
            replace_tuple(case["result"])

        return [cls(**case) for case in cases]


class TestDFA(unittest.TestCase):
    def __init__(self, test_method, input, colored_dfa=None):
        unittest.TestCase.__init__(self, test_method)

        self.input = input
        self.colored_dfa = colored_dfa

    def test_color(self):
        nfa = self.load_nfa()
        dfa = DFA(nfa)
        dfa._DFA__color()
        self.assertListEqual(sorted(dfa.dump()), sorted(self.colored_dfa))

    def load_nfa(self):
        nfa = NFA('')
        nodes = {}

        for u, ch, v, is_stop in self.input:
            if u not in nodes:
                nodes[u] = AutomatonNode(u)

            if v not in nodes:
                nodes[v] = AutomatonNode(v)

            nodes[u].add(ch, nodes[v])
            nodes[v].is_stop = bool(is_stop)

        nfa.root = nodes[0]
        return nfa

    @classmethod
    def load_cases(cls):
        cases = load_yaml("dfa_cases.yaml")
        for case in cases:
            replace_tuple(case["input"])
            replace_tuple(case["colored_dfa"])

        return [cls(**case) for case in cases]


def load_yaml(file_name):
    with file(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return [x for x in yaml.load_all(f.read())][0]


def replace_tuple(list):
    for i in xrange(0, len(list)):
        list[i] = tuple(list[i])
