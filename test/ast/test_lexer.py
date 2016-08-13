# -*- coding: utf-8 -*
"""
Lexer testcases

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import unittest
import os
import yaml

from expy.ast.lexer import Lexer


class TestLexer(unittest.TestCase):
    def __init__(self, raw, tokens):
        unittest.TestCase.__init__(self, "test_lexer")
        self.raw = raw
        self.tokens = tokens

    def test_lexer(self):
        lexer = Lexer(self.raw)

        result = []
        while lexer.peek():
            result.append(str(lexer.next()))

        self.assertListEqual(self.tokens, result)

    @classmethod
    def load_cases(cls):
        return [cls(**case) for case in load_yaml("lexer_cases.yaml")]


def load_yaml(file_name):
    with file(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return [x for x in yaml.load_all(f.read())][0]
