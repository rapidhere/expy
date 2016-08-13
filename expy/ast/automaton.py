# -*- coding: utf-8 -*-
"""
Automaton for build regular languages into tables

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"
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
        get successors by char
        """
        return self.successors[ch]

    def get_one(self, ch):
        """
        get on successor by char
        """
        if ch in self.successors:
            return self.successors[ch][0]
        else:
            return None

    def __hash__(self):
        return self.index

    def __str__(self):
        return "Node@ " + str(self.index)

    def __repr__(self):
        return self.__str__()


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

    build from a nfa
    """
    def __init__(self, nfa):
        Automaton.__init__(self)
        self.nfa = nfa

    def to_table(self):
        """
        Color and reduce the nfa to a dfa,
        and convert the dfa to a transfer table
        """
        self.__color()
        self.__reduce()

    def __color(self):
        # calc empty closure
        self.__get_all_empty_closure(self.nfa.root)

        state_map = {}
        changed_states = []

        root_closure = self.nfa.root.empty_closure
        root_hash = self.__hash_state(root_closure)
        changed_states.append(root_hash)
        state_map[root_hash] = {
            self.EMPTY_CH: root_closure,
            "index": 0}
        self.node_idx = 0

        # calc closures
        while changed_states:
            state_hash = changed_states.pop(-1)
            cur_map = state_map[state_hash]
            state = cur_map[self.EMPTY_CH]

            for s in state:
                for ch in s.successors.keys():
                    if ch not in cur_map:
                        cur_closure = self.__calc_closure(ch, state)
                        cur_hash = self.__hash_state(cur_closure)
                        cur_map[ch] = (cur_hash, cur_closure)

                        if cur_hash not in state_map:
                            self.node_idx += 1
                            state_map[cur_hash] = {
                                self.EMPTY_CH: cur_closure,
                                "index": self.node_idx}
                            changed_states.append(cur_hash)

        nodes = [AutomatonNode(x) for x in range(self.node_idx + 1)]
        # build DFA
        for state in state_map.values():
            u = nodes[state["index"]]

            for v in state[self.EMPTY_CH]:
                if v.is_stop:
                    u.is_stop = True
                    break

            for ch, s in state.items():
                if ch == "index" or ch == self.EMPTY_CH:
                    continue

                if ch not in u.successors:
                    u.add(ch, nodes[state_map[s[0]]["index"]])
        # set root, clear
        self.root = nodes[0]

    def __reduce(self):
        pass

    def __hash_state(self, state):
        return hash("`".join([str(x.index) for x in state]))

    def __calc_closure(self, ch, empty_closure):
        ret = set()
        for u in empty_closure:
            if ch in u.successors:
                for child in u.get(ch):
                    ret = ret.union(child.empty_closure)
        return ret

    def __get_all_empty_closure(self, node):
        if hasattr(node, "empty_closure"):
            return

        node.empty_closure = set()
        self.__get_empty_closure(node, node.empty_closure)

        for succ in node.successors.values():
            for u in succ:
                self.__get_all_empty_closure(u)

    def __get_empty_closure(self, node, closure):
        if node in closure:
            return
        closure.add(node)

        if self.EMPTY_CH in node.successors:
            for child in node.get(self.EMPTY_CH):
                self.__get_empty_closure(child, closure)


def to_table(regex):
    """
    Convert a regex to a transfer table
    """
    nfa = NFA(regex).parse()
    return DFA(nfa).to_table()
