#-*- coding: utf-8 -*-
"""
Compiled stub

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import struct
from opcode import opmap
import dis

from expy.exception import TooManyConstants
from expy import const


def invoke(f):
    def _f(self, *args, **kwargs):
        byte_codes = f(self, *args, **kwargs)
        if isinstance(byte_codes, tuple):
            for b in byte_codes:
                self._bytecodes.append(b)
        else:
            self._bytecodes.append(byte_codes)
        return byte_codes

    _f.__name__ = f.__name__
    return _f


class CompiledStub(object):
    """
    Compiled stub binary
    """
    def __init__(self, expression):
        self.expression = expression
        self.__hash = hash(expression)

        # None is always the first const
        self._constants_map = {}
        self._consts = [None]
        self._bytecodes = []

        self._code = None

    def __hash__(self):
        return self.__hash

    def pack(self, filename, stacksize=32):
        """
        Pack a compiled code object for execute

        :pack_print: pack print info instructions in code object
        """
        # pack return instruction
        self.invoke_store_global(0)
        self.invoke_load_const(None)
        self.invoke_return_value()

        # pack code object
        self._code = self._gen_code(
            0,                                  # argcount
            1,                                  # nlocals
            stacksize,                          # statcksize
            64,                                 # TODO: flag
            ''.join(self._bytecodes),           # codes
            tuple(self._consts),                # consts
            (const.Stub.RET_VARNAME,),          # names
            (),                                 # varnames
            filename,                           # filename
            "<expy stub @ %s>" % self.__hash,   # name of module
            1,                                  # lineno
            '',                                 # lnotab
            (),                                 # freevars, for closures
            ())                                 # cellvars

        # clear
        self._consts = None
        self._bytecodes = None

    def execute(self):
        """
        Execute the stub
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        ctx = {}
        exec self._code in ctx

        return ctx[const.Stub.RET_VARNAME]

    def add_const(self, const):
        """
        add a constant
        """
        if const in self._constants_map:
            return

        if self.n_const >= 65536:
            raise TooManyConstants()

        self._consts.append(const)
        self._constants_map[const] = self.n_const - 1

    @property
    def n_const(self):
        """
        get number of constants
        """
        return len(self._consts)

    def dis_code_object(self):
        """
        dump the code packed code object
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        dis.dis(self._code)

    @property
    def code(self):
        """
        Det packed code
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        return self._code

    # ~ bytecode invoking helpers
    @invoke
    def invoke_load_const(self, const):
        idx = self._get_constant_index(const)
        if idx is None:
            self.add_const(const)
            idx = self._get_constant_index(const)

        return (
            struct.pack("B", opmap["LOAD_CONST"]),
            struct.pack("H", idx))  # NOTE: number of const cannot exceed 65536

    @invoke
    def invoke_binary_add(self):
        return struct.pack("B", opmap["BINARY_ADD"])

    @invoke
    def invoke_binary_subtract(self):
        return struct.pack("B", opmap["BINARY_SUBTRACT"])

    @invoke
    def invoke_binary_multiple(self):
        return struct.pack("B", opmap["BINARY_MULTIPLY"])

    @invoke
    def invoke_binary_divide(self):
        return struct.pack("B", opmap["BINARY_DIVIDE"])

    @invoke
    def invoke_print_item(self):
        return struct.pack("B", opmap["PRINT_ITEM"])

    @invoke
    def invoke_print_newline(self):
        return struct.pack("B", opmap["PRINT_NEWLINE"])

    @invoke
    def invoke_return_value(self):
        return struct.pack("B", opmap["RETURN_VALUE"])

    @invoke
    def invoke_unary_negative(self):
        return struct.pack("B", opmap["UNARY_NEGATIVE"])

    @invoke
    def invoke_unary_positive(self):
        return struct.pack("B", opmap["UNARY_POSITIVE"])

    @invoke
    def invoke_store_fast(self, var_index):
        return (
            struct.pack("B", opmap["STORE_FAST"]),
            struct.pack("H", var_index))

    @invoke
    def invoke_store_global(self, var_index):
        return (
            struct.pack("B", opmap["STORE_GLOBAL"]),
            struct.pack("H", var_index))

    # ~ other helpers
    def _gen_code(self, *args):
        # a trick to get code object
        def __useless():
            return
        return type(__useless.__code__)(*args)

    def _get_constant_index(self, const):
        if const is None:
            return 0
        return self._constants_map.get(const)
