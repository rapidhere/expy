# -*- coding: utf-8 -*-
"""
Automaton for build regular languages into tables

Author: rapidhere@gmail.com
"""

__author__ = "rapidhere"
__all__ = ["to_table"]


class AutomatonNode(object):
    """
    Represent a Automaton's Node
    """
    def __init__(self, index, is_stop=False):
        self.successors = {}
        self.index = index
        self.is_stop = is_stop

    def add(self, ch, node):
        """
        Append a node as this node's successor

        return the appended node
        """
        if ch not in self.successors:
            self.successors[ch] = []

        self.successors[ch].append(node)

        return node

    def get(self, ch):
        """
        get a successor by char
        """
        return self.successors[ch]


class Automaton(object):
    """
    Abstract Automaton

    Provided some common tools for Automaton
    """
    EMPTY_CH = '`'

    def __init__(self):
        self.node_idx = 0
        self.root = self.alloc_node()

        # for dump usage
        self.__visited = None

    def dump(self):
        """
        dump the Automaton as a graph
        """
        self.__visited = set()
        ret = []
        self.__dump_node(self.root, ret)

        return ret

    def alloc_node(self):
        """
        Alloc a Automaton node
        """
        self.node_idx += 1
        return AutomatonNode(self.node_idx - 1)

    def __dump_node(self, node, ret):
        if node.index in self.__visited:
            return

        self.__visited.add(node.index)

        for ch in node.successors.keys():
            for child in node.get(ch):
                ret.append((node.index, ch, child.index, 1 if child.is_stop else 0))
                self.__dump_node(child, ret)


class NFA(Automaton):
    """
    Nod-determined Finite state Automaton

    build from a regular expression
    """
    def __init__(self, regex):
        Automaton.__init__(self)

        self.regex = regex
        self.idx = 0
        self.length = len(self.regex)

    def parse(self):
        """
        parse the regex to DFA

        return the builded DFA
        """
        tail = self.__concat(self.root)
        tail.is_stop = True

        return self

    def __concat(self, cur):
        while self.idx < self.length:
            ch = self.__peek()

            if ch == '\\':
                self.__next()
                cur = self.__single(cur)
            elif ch == '(':
                cur = self.__loop(cur)
            elif ch == '[':
                cur = self.__choice(cur)
            elif ch in (',', ']', ')'):
                break
            else:
                cur = self.__single(cur)

        return cur

    def __single(self, cur):
        return cur.add(self.__next(), self.alloc_node())

    def __choice(self, start):
        self.__next()  # read up leading '['
        end = self.alloc_node()

        while True:
            tmp = self.alloc_node()
            start.add(self.EMPTY_CH, tmp)
            self.__concat(tmp).add(self.EMPTY_CH, end)

            if self.__peek() == ']':
                break
            assert self.__next() == ','

        assert self.__next() == ']'
        return end

    def __loop(self, start):
        self.__next()  # read up leading '('
        end = self.alloc_node()
        end.add(self.EMPTY_CH, start)
        start.add(self.EMPTY_CH, end)

        tmp = self.alloc_node()
        start.add(self.EMPTY_CH, tmp)
        self.__concat(tmp).add(self.EMPTY_CH, end)

        assert self.__next() == ')'
        return end

    def __next(self):
        self.idx += 1
        return self.regex[self.idx - 1]

    def __peek(self):
        return self.regex[self.idx]


class DFA(Automaton):
    """
    Determined Finite state Automaton

    build from a dfa
    """
    def __init__(self, dfa):
        Automaton.__init__(self)
        self.dfa = dfa

    def reduce(self):
        pass
        return self

    def to_table(self):
        self.reduce()
        pass


def to_table(regex):
    """
    Convert a regex to a transfer table
    """
    nfa = NFA(regex).parse()
    return DFA(nfa).to_table()
