# -*- coding: utf-8 -*
"""
Parse testcases

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import unittest
import os
import yaml

from expy.ast.parser import Parser


class TestParser(unittest.TestCase):
    def __init__(self, expression, ast):
        unittest.TestCase.__init__(self, "test_parse")
        self.expression = expression
        self.ast = ast

    def test_parse(self):
        ast = Parser().parse(self.expression)

        self.assertDictEqual(self.ast, ast.dump())

    @classmethod
    def load_cases(cls):
        return [cls(**case) for case in load_yaml("parser_cases.yaml")]


def load_yaml(file_name):
    with file(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return [x for x in yaml.load_all(f.read())][0]
