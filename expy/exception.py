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


class ExpySyntaxError(Exception):
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