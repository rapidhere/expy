#-*- coding: utf-8 -*-
"""
Compiled stub

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import struct
from opcode import opmap
import dis

from expy.exception import TooManyConstants, TooManyVariables
from expy import const


# dec
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
        self._consts = [None]
        self._global_vars = [const.Stub.RET_VARNAME]
        self._local_vars = []

        self._bytecodes = []

        self._code = None

    def __hash__(self):
        return self.__hash

    def pack(self, filename, stacksize=32):
        """
        Pack a compiled code object for execute

        :pack_print: pack print info instructions in code object
        """
        precode = []
        # load ctx into fast
        for li in xrange(len(self._local_vars)):
            var = self._local_vars[li]
            gi = self._get_global_variable_index_or_store(var)

            c1, c2 = self._invoke_load_global_by_idx(gi)
            c3, c4 = self._invoke_store_fast_by_idx(li)

            precode.append(c1)
            precode.append(c2)
            precode.append(c3)
            precode.append(c4)

        # prepend pre code
        self._bytecodes = precode + self._bytecodes

        # pack return instruction
        self.invoke_store_global(const.Stub.RET_VARNAME)
        self.invoke_load_const(None)
        self.invoke_return_value()

        # pack code object
        self._code = self._gen_code(
            0,                                  # argcount
            self.n_local_var,                   # nlocals
            stacksize,                          # statcksize
            0,                                  # TODO: flag
            ''.join(self._bytecodes),           # codes
            tuple(self._consts),                # consts
            tuple(self._global_vars),           # names
            tuple(self._local_vars),            # varnames
            filename,                           # filename
            "<expy stub @ %s>" % self.__hash,   # name of module
            1,                                  # lineno
            '',                                 # lnotab
            (),                                 # freevars, for closures
            ())                                 # cellvars

        # clear
        self._consts = None
        self._bytecodes = None
        self._global_vars = None
        self._local_vars = None

    def execute(self, **ctx):
        """
        Execute the stub
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        exec self._code in ctx

        return ctx[const.Stub.RET_VARNAME]

    @property
    def n_const(self):
        """
        get number of constants
        """
        return len(self._consts)

    @property
    def n_global_var(self):
        """
        get number of global variables
        """
        return len(self._global_vars)

    @property
    def n_local_var(self):
        """
        get number of local variables
        """
        return len(self._local_vars)

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
        idx = self._get_constant_index_or_store(const)
        return self._invoke_load_const_by_idx(idx)

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
    def invoke_binary_modulo(self):
        return struct.pack("B", opmap["BINARY_MODULO"])

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
    def invoke_store_fast(self, var_name):
        idx = self._get_local_variable_index_or_store(var_name)
        return self._invoke_store_fast_by_idx(idx)

    @invoke
    def invoke_load_fast(self, var_name):
        idx = self._get_local_variable_index_or_store(var_name)
        return (
            struct.pack("B", opmap["LOAD_FAST"]),
            struct.pack("H", idx))

    @invoke
    def invoke_store_global(self, var_name):
        idx = self._get_global_variable_index_or_store(var_name)

        return (
            struct.pack("B", opmap["STORE_GLOBAL"]),
            struct.pack("H", idx))

    @invoke
    def invoke_load_global(self, var_name):
        idx = self._get_global_variable_index_or_store(var_name)
        return self._invoke_load_global_by_idx(idx)

    # ~ other helpers
    def _gen_code(self, *args):
        # a trick to get code object
        def __useless():
            return
        return type(__useless.__code__)(*args)

    def _invoke_load_const_by_idx(self, idx):
        return (
            struct.pack("B", opmap["LOAD_CONST"]),
            struct.pack("H", idx))

    def _invoke_load_global_by_idx(self, idx):
        return (
            struct.pack("B", opmap["LOAD_GLOBAL"]),
            struct.pack("H", idx))

    def _invoke_store_fast_by_idx(self, idx):
        return (
            struct.pack("B", opmap["STORE_FAST"]),
            struct.pack("H", idx))

    def _get_constant_index_or_store(self, const):
        try:
            return self._consts.index(const)
        except ValueError:
            if self.n_const >= 65536:
                raise TooManyConstants()

            self._consts.append(const)
            return self.n_const - 1

    def _get_global_variable_index_or_store(self, var_name):
        try:
            return self._global_vars.index(var_name)
        except ValueError:
            if self.n_global_var >= 65536:
                raise TooManyVariables()

            self._global_vars.append(var_name)
            return self.n_global_var - 1

    def _get_local_variable_index_or_store(self, var_name):
        try:
            # var_name = "_" + var_name
            return self._local_vars.index(var_name)
        except ValueError:
            if self.n_local_var >= 65536:
                raise TooManyVariables()

            self._local_vars.append(var_name)
            return self.n_local_var - 1
