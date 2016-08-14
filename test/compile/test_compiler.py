# -*- coding: utf-8 -*-
"""
Compiler Test

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

from expy.compile.compiler import Compiler

import unittest
import os
import yaml


class TestCompiler(unittest.TestCase):
    def __init__(self, expression, result, variables=None):
        unittest.TestCase.__init__(self, "test_compile")
        self.expression = expression
        self.result = result

        if variables is None:
            self.variables = {}
        else:
            self.variables = variables

    def test_compile(self):
        comp = Compiler()
        stub = comp.compile(self.expression)

        self.assertEqual(stub.execute(**self.variables), self.result)

    @classmethod
    def load_cases(cls):
        return [cls(**case) for case in load_yaml("compiler_cases.yaml")]


def load_yaml(file_name):
    with file(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return [x for x in yaml.load_all(f.read())][0]
