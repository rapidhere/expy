# -*- coding: utf-8 -*
"""
Lexer

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"
__all__ = ["Lexer"]

from token import tokens

from expy.exception import UnexpectedCharacter


class Lexer(object):
    """
    Expression lexer
    """
    def __init__(self, raw):
        self.raw = raw
        self.pos = 0
        self.end = len(raw)
        self.__accepted = []

    def __accept_next(self):
        for token_matcher in tokens:
            token = token_matcher.match(self.raw, self.pos, self.end)

            if token:
                self.pos = token.end_pos
                return token

        # accept fail
        if self.pos >= self.end:
            return None  # return None if no more character can be accepted
        else:
            raise UnexpectedCharacter(self.pos, self.raw[self.pos])

    def next(self):
        """
        get current token, and step to next
        """
        if not self.__accepted:
            self.__accepted.append(self.__accept_next())

        return self.__accepted.pop(-1)

    def peek(self):
        """
        get current token withou stepping to next
        """
        if not self.__accepted:
            self.__accepted.append(self.__accept_next())

        return self.__accepted[-1]
