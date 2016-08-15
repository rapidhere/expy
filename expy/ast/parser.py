# -*- coding: utf-8 -*
"""
Parser

Expression Specifications:

EXPRESSION =
  | BINARY_EXPRESSION

BINARY_EXPRESSION =
  | BINARY_EXPRESSION + BINARY_EXPRESSION
  | BINARY_EXPRESSION - BINARY_EXPRESSION
  | BINARY_EXPRESSION * BINARY_EXPRESSION (mind priority)
  | BINARY_EXPRESSION / BINARY_EXPRESSION (mind priority)
  | BINARY_EXPRESSION % BINARY_EXPRESSION (mind priority)
  | UNARY_EXPRESSION

UNARY_EXPRESSION =
  | - EXPRESSION
  | + EXPRESSION
  | SINGLE_EXPRESSION

SINGLE_EXPRESSION =
  | PRIMARY_EXPRESSION
  | FUNCTION_CALL_EXPRESSION

FUNCTION_CALL_EXPRESSION =
  | ID ( expression0, expression1 ... )

PRIMARY_EXPRESSION =
  | NUMBER
  | ID

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

from lexer import Lexer
from token import Number, Plus, Minus, Multiple, Divide, Mod, Id, LeftParenthesis, RightParenthesis, Comma
from absyn import PrimaryExpression, BinaryExpression, UnaryExpression, FunctionCallExpression

from expy.exception import UnexpectedToken


class Parser(object):
    """
    Expression Parser
    """
    def __init__(self):
        self.lexer = None

    def parse(self, expression):
        """
        parse the expression and return a ast
        """
        self.lexer = Lexer(expression)

        return self._parse_expression()

    def _parse_expression(self):
        return self._parse_binary_expression()

    def _parse_binary_expression(self):
        op_stack = []
        ex_stack = []

        def pop_op_stack(cur_op):
            while len(op_stack) and (not cur_op or cur_op.binop_priority <= op_stack[-1].binop_priority):
                right = ex_stack.pop(-1)
                left = ex_stack.pop(-1)
                op = op_stack.pop(-1)
                ex_stack.append(BinaryExpression(op, left, right))

        # append first expression
        ex_stack.append(self._parse_unary_expression())

        while True:
            op = self._next_binary_op()
            if op is None:
                break
            pop_op_stack(op)
            op_stack.append(op)

            exp = self._parse_unary_expression()
            ex_stack.append(exp)

        pop_op_stack(None)

        return ex_stack[0]

    def _parse_unary_expression(self):
        token = self.lexer.peek()

        if token == Plus or token == Minus:
            self.lexer.next()
            # can only be unary expression here
            exp = self._parse_unary_expression()
            return UnaryExpression(token, exp)
        else:
            return self._parse_single_expression()

    def _parse_single_expression(self):
        token = self.lexer.next()

        if token not in (Number, Id):
            raise UnexpectedToken(token)

        if token != Number and self.lexer.peek() == LeftParenthesis:
            args = []

            while not self.lexer.peek() == RightParenthesis:
                self.lexer.next()
                args.append(self._parse_expression())

                comma = self.lexer.peek()
                if comma not in (Comma, RightParenthesis):
                    raise UnexpectedToken(comma)
            self.lexer.next()
            return FunctionCallExpression(token, args)
        else:
            return PrimaryExpression(token)

    def _next_binary_op(self):
        if self.lexer.peek() not in (Plus, Minus, Multiple, Divide, Mod):
            return None
        return self.lexer.next()
