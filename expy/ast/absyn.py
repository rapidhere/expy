# -*- coding: utf-8 -*
"""
Abstract Syntax Tree Components

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"


class BaseAbstractSyntax(object):
    """
    Base Abstract Syntax Tree Component
    """
    def __init__(self):
        pass

    def __eq__(self, another):
        return isinstance(another, self.__class__) or issubclass(another, self.__class__)

    def __ne__(self, another):
        return not self.__eq__(another)

    @property
    def position(self):
        """
        get the position of the component
        """
        raise NotImplementedError("cannot decide the position of this component")

    def dump(self):
        """
        dump component
        """
        raise NotImplementedError("cannot dump")


class Expression(BaseAbstractSyntax):
    """
    Expression Component
    """
    pass


class BinaryExpression(Expression):
    """
    Binary operator expression
    """
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def position(self):
        return self.left.position

    def dump(self):
        return {
            "class": self.__class__.__name__,
            "operator": self.operator.value,
            "left": self.left.dump(),
            "right": self.right.dump()}


class UnaryExpression(Expression):
    """
    Unary operator expression
    """
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def position(self):
        return self.operator.position

    def dump(self):
        return {
            "class": self.__class__.__name__,
            "operator": self.operator.value,
            "expression": self.expression.dump()}


class PrimaryExpression(Expression):
    """
    Simple and Primary Expression Component
    """
    def __init__(self, token):
        self.token = token

    def position(self):
        return self.token.start_pos

    def dump(self):
        return {
            "class": self.__class__.__name__,
            "token": self.token.value}


class FunctionCallExpression(Expression):
    """
    Function call expression
    """
    def __init__(self, id, args):
        self.id = id
        self.arguments = args

    def position(self):
        return self.id.start_pos

    def dump(self):
        return {
            "class": self.__class__.__name__,
            "id": self.id.value,
            "arguments": [arg.dump() for arg in self.arguments]}
