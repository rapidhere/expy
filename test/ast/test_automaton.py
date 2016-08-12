# -*- coding: utf-8 -*

import unittest

from expy.ast.automaton import NFA


class TestNFA(unittest.TestCase):
    def __init__(self, descrption, regex, result):
        unittest.TestCase.__init__(self, "test_parse")

        self.descrption = descrption
        self.regex = regex
        self.result = sorted(result)

    def test_parse(self):
        nfa = NFA(self.regex).parse()
        self.assertListEqual(sorted(nfa.dump()), self.result)

    @classmethod
    def load_cases(cls):
        return [cls(*case) for case in cls.CASES]

    # Write test cases here
    CASES = (
        ("normal", "abcd", (
            (0, 'a', 1, 0),
            (1, 'b', 2, 0),
            (2, 'c', 3, 0),
            (3, 'd', 4, 1))),

        ("choice", "[a,b,c,d]", (
            (0, '`', 2, 0),
            (0, '`', 4, 0),
            (0, '`', 6, 0),
            (0, '`', 8, 0),
            (3, '`', 1, 1),
            (5, '`', 1, 1),
            (7, '`', 1, 1),
            (9, '`', 1, 1),
            (2, 'a', 3, 0),
            (4, 'b', 5, 0),
            (6, 'c', 7, 0),
            (8, 'd', 9, 0))),

        ("loop", "(abc)", (
            (0, '`', 1, 1),
            (0, '`', 2, 0),
            (2, 'a', 3, 0),
            (3, 'b', 4, 0),
            (4, 'c', 5, 0),
            (5, '`', 1, 1),
            (1, '`', 0, 0))),

        ("concat-loop", "a(b)c", (
            (0, 'a', 1, 0),
            (1, '`', 2, 0),
            (2, '`', 1, 0),
            (2, 'c', 5, 1),
            (1, '`', 3, 0),
            (3, 'b', 4, 0),
            (4, '`', 2, 0))),

        ("concat-choice", "a[b,c]d", (
            (0, 'a', 1, 0),
            (1, '`', 3, 0),
            (1, '`', 5, 0),
            (3, 'b', 4, 0),
            (5, 'c', 6, 0),
            (4, '`', 2, 0),
            (6, '`', 2, 0),
            (2, 'd', 7, 1))),

        ("choice-loop", "[(a),(bc),d]", (
            (0, '`', 2, 0),
            (0, '`', 6, 0),
            (0, '`', 11, 0),
            (2, '`', 3, 0),
            (2, '`', 4, 0),
            (3, '`', 2, 0),
            (3, '`', 1, 1),
            (4, 'a', 5, 0),
            (5, '`', 3, 0),
            (6, '`', 7, 0),
            (6, '`', 8, 0),
            (7, '`', 1, 1),
            (7, '`', 6, 0),
            (8, 'b', 9, 0),
            (9, 'c', 10, 0),
            (10, '`', 7, 0),
            (11, 'd', 12, 0),
            (12, '`', 1, 1))),

        ("complex - 1", "a(a)[a,b,c]de", (
            (0, 'a', 1, 0),
            (1, '`', 2, 0),
            (2, '`', 1, 0),
            (2, '`', 6, 0),
            (6, 'a', 7, 0),
            (7, '`', 5, 0),
            (5, 'd', 12, 0),
            (12, 'e', 13, 1),
            (2, '`', 8, 0),
            (8, 'b', 9, 0),
            (9, '`', 5, 0),
            (2, '`', 10, 0),
            (10, 'c', 11, 0),
            (11, '`', 5, 0),
            (1, '`', 3, 0),
            (3, 'a', 4, 0),
            (4, '`', 2, 0))))
