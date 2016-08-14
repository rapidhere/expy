# -*- coding: utf-8 -*
"""
Exceptions

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"


class ExpyException(Exception):
    """
    Base Exception
    """


class ExpyCompilingError(ExpyException):
    """
    Generic compiling errors
    """


class ExpySyntaxError(ExpyCompilingError):
    """
    Generic syntax errors
    """


class UnexpectedCharacter(ExpySyntaxError):
    """
    Unexpected Character
    """
    def __init__(self, pos, char):
        ExpySyntaxError.__init__(self, "unexpected character `%s` at: %d" % (char, pos))


class UnexpectedEOF(ExpySyntaxError):
    """
    Unexpected end of file
    """
    def __init__(self):
        ExpySyntaxError.__init__(self, "unexpected end of file")


class UnexpectedToken(ExpySyntaxError):
    """
    Unexpected Token
    """
    def __init__(self, token):
        ExpySyntaxError.__init__(
            self, "unexpected token %s `%s` at %d" %
            (token.__class__.__name__, str(token.value), token.start_pos))


class UnsupportedExpression(ExpyCompilingError):
    """
    this class of expression is not supported
    """
    def __init__(self, exp):
        ExpyCompilingError.__init__(
            self, "%s is not supported yet" % exp.__class__.__name__)


class UnsupportedOperator(ExpyCompilingError):
    """
    cannot compile this operator
    """
    def __init__(self, op):
        ExpyCompilingError.__init__(
            self, "operator %s is not supported yet" % op.value)


class UnsupportedValueType(ExpySyntaxError):
    """
    this type of value is not supported
    """
    def __init__(self, token):
        ExpyCompilingError.__init__(
            self, "value `%s` of type %s is not supported yet" % (token.value, token.__class__.__name__))


class TooManyConstants(ExpySyntaxError):
    """
    number of constants exceeded 65536
    """
    def __init__(self):
        ExpyCompilingError.__init__(
            self, "too many constants in the expression!")
