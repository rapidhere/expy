#-*- coding: utf-8 -*-
"""
Compiler

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

from compiled_stub import CompiledStub
from function import check_and_invoke_function

from expy.ast import Parser
from expy.ast.absyn import BinaryExpression, UnaryExpression, PrimaryExpression, FunctionCallExpression
from expy.ast.token import Number, Minus, Plus, Divide, Multiple, Mod, Id
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
        self._do_compile(ast, stub)
        self.store_stub(expression, stub)

        # pack the stub for next executing or dumping
        stub.pack(const.Stub.STUB_FILENAME, **kwargs)

        return stub
    
    def _do_compile(self, ast, stub):
        stack = []
        
        # init stack
        stack.append(self._compile_expression(ast, stub))

        while stack:
            topf = stack.pop(-1)

            try:
                nextf = topf.next()
                stack.append(topf)
                if nextf is not None:
                    stack.append(nextf)
            except StopIteration:
                pass
    
    def _compile_expression(self, ast, stub):
        if ast == BinaryExpression:
            yield self._compile_binary_expression(ast, stub)
        elif ast == UnaryExpression:
            yield self._compile_unary_expression(ast, stub)
        elif ast == PrimaryExpression:
            yield self._compile_primary_expression(ast, stub)
        elif ast == FunctionCallExpression:
            yield self._compile_function_call_expression(ast, stub)
        else:
            raise UnsupportedExpression(ast)
    
    def _compile_function_call_expression(self, ast, stub):
        for arg_exp in ast.arguments:
            yield self._compile_expression(arg_exp, stub)

        check_and_invoke_function(ast.id.value, ast.arguments, stub)
    
    def _compile_binary_expression(self, ast, stub):
        op = ast.operator
        yield self._compile_expression(ast.left, stub)
        yield self._compile_expression(ast.right, stub)

        if op == Plus:
            stub.invoke_binary_add()
        elif op == Minus:
            stub.invoke_binary_subtract()
        elif op == Divide:
            stub.invoke_binary_divide()
        elif op == Multiple:
            stub.invoke_binary_multiple()
        elif op == Mod:
            stub.invoke_binary_modulo()
        else:
            raise UnsupportedOperator(op)
    
    def _compile_unary_expression(self, ast, stub):
        op = ast.operator
        yield self._compile_expression(ast.expression, stub)

        if op == Plus:
            stub.invoke_unary_positive()
        elif op == Minus:
            stub.invoke_unary_negative()
        else:
            raise UnsupportedOperator(op)
    
    def _compile_primary_expression(self, ast, stub):
        token = ast.token
        if token == Number:
            stub.invoke_load_const(token.value)
        elif token == Id:
            stub.invoke_load_fast(token.value)
        else:
            raise UnsupportedValueType(token)
