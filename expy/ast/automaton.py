# -*- coding: utf-8 -*-
"""
Automaton for build regular languages into tables

Author: rapidhere@gmail.com
"""

__author__ = "rapidhere"
__all__ = ["to_table"]


class AutomatonNode(object):
    def __init__(self, is_stop=False):
        self.successors = {}
        self.is_stop = is_stop

    def add(self, ch, node):
        if ch not in self.successors:
            self.successors[ch] = []

        self.successors[ch].append(node)

    def get(self, ch):
        return self.successors[ch]


class NFA(object):
    EMPTY_CH = '`'

    def __init__(self, regex):
        self.regex = regex
        self.root = AutomatonNode()
        self.idx = 0
        self.length = len(self.regex)

    def parse(self):
        tail = self.concat(self.root)
        tail.is_stop = True

        return self

    def concat(self, cur):
        while self.idx < self.length:
            ch = self.peek()

            if ch == '\\':
                self.next()
                cur = self.single(cur)
            elif ch == '(':
                cur = self.loop(cur)
            elif ch == '[':
                cur = self.choice(cur)
            elif ch in (',', ']', ')'):
                break
            else:
                cur = self.single(cur)

        return cur

    def single(self, cur):
        return cur.add(self.next(), AutomatonNode())

    def choice(self, start):
        self.next()  # read up leading '['
        end = AutomatonNode()

        while True:
            start.add(self.EMPTY_CH, self.concat(AutomatonNode)).add(self.EMPTY_CH, end)

            if self.peek() == ']':
                break
            assert self.next() == ','

        assert self.next() == ']'
        return end

    def loop(self, start):
        self.next()  # read up leadning '('
        end = AutomatonNode()
        end.add(self.EMPTY_CH, start)

        start.add(self.EMPTY_CH, self.concat(AutomatonNode())).add(self.EMPTY_CH, end)

        assert self.next() == ')'
        return end

    def next(self):
        self.idx += 1
        return self.regex[self.idx - 1]

    def peek(self):
        return self.regex[self.idx]


class DFA(object):
    def __init__(self, dfa):
        self.dfa = dfa

    def reduce(self):
        pass
        return self

    def to_table(self):
        self.reduce()
        pass


def to_table(regex):
    nfa = NFA(regex).parse()
    return DFA(nfa).to_table()
