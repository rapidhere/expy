#-*- coding: utf-8 -*-
"""
Compiler

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

from compiled_stub import CompiledStub

from expy.ast import Parser
from expy.ast.absyn import BinaryExpression, UnaryExpression, PrimaryExpression
from expy.ast.token import Number, Minus, Plus
from expy.exception import UnsupportedExpression, UnsupportedOperator, UnsupportedValueType
from expy import const


class Compiler(object):
    """
    the Compiler
    """
    def __init__(self):
        self._compiled_store = {}
        self._parser = Parser()

    def get_stub(self, expression):
        """
        get a compiled stub
        """
        return self._compiled_store.get(expression)

    def store_stub(self, expression, stub):
        """
        store a compiled stub
        """
        self._compiled_store[expression] = stub

    def compile(self, expression, **kwargs):
        """
        compile a expession, and return a compiled stub which can execute
        """
        # find for stored stub
        stub = self.get_stub(expression)
        if stub:
            return stub

        # compile and store a new one
        ast = self._parser.parse(expression)
        stub = CompiledStub(expression)
        self._compile_expression(ast, stub)
        self.store_stub(expression, stub)

        # pack the stub for next executing or dumping
        stub.pack(const.Stub.STUB_FILENAME, **kwargs)

        return stub

    def _compile_expression(self, ast, stub):
        if ast == BinaryExpression:
            return self._compile_binary_expression(ast, stub)
        elif ast == UnaryExpression:
            return self._compile_unary_expression(ast, stub)
        elif ast == PrimaryExpression:
            return self._compile_primary_expression(ast, stub)
        else:
            raise UnsupportedExpression(ast)

    def _compile_binary_expression(self, ast, stub):
        op = ast.operator
        self._compile_expression(ast.left, stub)
        self._compile_expression(ast.right, stub)

        if op == Plus:
            stub.invoke_binary_add()
        elif op == Minus:
            stub.invoke_binary_subtract()
        else:
            raise UnsupportedOperator(op)

    def _compile_unary_expression(self, ast, stub):
        raise UnsupportedExpression(ast)

    def _compile_primary_expression(self, ast, stub):
        token = ast.token
        if token == Number:
            stub.invoke_load_const(token.value)
        else:
            raise UnsupportedValueType(token)
