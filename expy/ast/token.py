# -*- coding: utf-8 -*
"""
Tokens

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"
__all__ = ["tokens"]

import types

from automaton import to_table


class Token(object):
    """
    Base token
    """
    regex = None
    _table = None

    def __init__(self, start_pos, end_pos, value):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.value = value.strip()

    def __str__(self):
        return "%s @ %d,%d" % (str(self.value), self.start_pos, self.end_pos)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, another_token):
        return isinstance(another_token, self.__class__) or issubclass(another_token, self.__class__)

    def __ne__(self, another_token):
        return not self.__eq__(another_token)

    @classmethod
    def _get_table(cls):
        if cls._table is None:
            cls._table = to_table(cls.regex)

        return cls._table

    @classmethod
    def match(cls, raw, pos, end):
        """
        accept a token from raw string

        return accepted token
        """
        status = 0
        table = cls._get_table()
        start = pos

        while True:
            if pos < end:
                next_status = table[status].get(raw[pos])
            else:
                next_status = None

            if next_status is None:
                if table[status]["is_stop"]:
                    return cls(start, pos, raw[start:pos])
                else:
                    return None
            status = next_status
            pos += 1


class Number(Token):
    """
    Float and Integer token
    """
    regex = "( )[0,1,2,3,4,5,6,7,8,9]([0,1,2,3,4,5,6,7,8,9])[.[0,1,2,3,4,5,6,7,8,9]([0,1,2,3,4,5,6,7,8,9]),( )]( )"

    def __init__(self, *args):
        Token.__init__(self, *args)

        if "." in self.value:
            self.value = float(self.value)
        else:
            self.value = int(self.value)

    @property
    def is_float(self):
        """
        determine wether this is a float value
        """
        return isinstance(self.value, types.FloatType)


class Id(Token):
    """
    A id
    """
    regex = (
        "( )[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,"
        "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,_]"
        "([a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,"
        "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,0,1,2,3,4,5,6,7,8,9,_])( )")


class Plus(Token):
    """
    Plus token
    """
    regex = "( )+( )"
    binop_priority = 0


class Minus(Token):
    """
    Minus token
    """
    regex = "( )-( )"
    binop_priority = 0


class Multiple(Token):
    """
    Multiple token
    """
    regex = "( )*( )"
    binop_priority = 1


class Divide(Token):
    """
    Divide token
    """
    regex = "( )/( )"
    binop_priority = 1


class Mod(Token):
    """
    Mod token
    """
    regex = "( )%( )"
    binop_priority = 1


class LeftParenthesis(Token):
    """
    Left Parenthesis token
    """
    regex = "( )\\(( )"


class RightParenthesis(Token):
    """
    Right Parenthesis token
    """
    regex = "( )\\)( )"


class Comma(Token):
    """
    Comma token
    """
    regex = "( )\\,( )"


tokens = (
    Plus,
    Minus,
    Multiple,
    Divide,
    Mod,
    Number,
    Id,
    LeftParenthesis,
    RightParenthesis,
    Comma)
