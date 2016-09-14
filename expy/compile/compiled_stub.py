# -*- coding: utf-8 -*-
"""
Compiled stub

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import struct
from opcode import opmap, cmp_op
import dis
import contextlib

from expy.exception import TooManyConstants, TooManyVariables
from expy import const


def append_byte(container, s):
    for c in s:
        container.append(c)


# dec
def invoke(f):
    def _f(self, *args, **kwargs):
        byte_codes = f(self, *args, **kwargs)
        if isinstance(byte_codes, tuple):
            for b in byte_codes:
                append_byte(self._bytecodes, b)
                self._cur_pos += len(b)
        else:
            append_byte(self._bytecodes, byte_codes)
            self._cur_pos += len(byte_codes)
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

        self._cur_pos = 0

        # None is always the first const
        self._consts = [None]
        self._global_vars = [const.Stub.RET_VARNAME]
        self._local_vars = []
        self._label_set_pos = {}
        self._label_invoke_pos = {}

        self._cur_stack_size = 0
        self._max_stack_size = 0

        self._bytecodes = []

        self._code = None

    def __hash__(self):
        return self.__hash

    def pack(self, filename, stacksize=-1):
        """
        Pack a compiled code object for execute

        :stacksize: specific the stacksize, set -1 to invoke auto stacksize
        """
        precode = []
        # load ctx into fast
        for li in xrange(len(self._local_vars)):
            var = self._local_vars[li]
            # ignore inner usage variables
            if var.startswith("__") and var.endswith("__"):
                continue

            gi = self._get_global_variable_index_or_store(var)

            c1, c2 = self._invoke_load_global_by_idx(gi)
            c3, c4 = self._invoke_store_fast_by_idx(li)

            append_byte(precode, c1)
            append_byte(precode, c2)
            append_byte(precode, c3)
            append_byte(precode, c4)

        # prepend pre code
        prelen = len(precode)
        self._bytecodes = precode + self._bytecodes

        # replace labels:
        for label in self._label_set_pos:
            for i in xrange(len(self._label_set_pos[label])):
                # get label set pos
                label_spos = self._label_set_pos[label][i]
                if label_spos < 0:
                    raise ValueError("label %s not seted" % label)

                # add prefix length, this is the real label set pos
                label_spos += prelen

                # get replace pos bytecode
                bpos = struct.pack("H", label_spos)

                # replace each label's invoke place
                for ipos in self._label_invoke_pos[label][i]:
                    ipos += prelen
                    self._bytecodes[ipos] = bpos[0]
                    self._bytecodes[ipos + 1] = bpos[1]

        # pack return instruction
        self.invoke_store_global(const.Stub.RET_VARNAME)
        self.invoke_load_const(None)
        self.invoke_return_value()

        # calc stacksize
        if stacksize < 0:
            stacksize = self._max_stack_size

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
        self._label_invoke_pos = None
        self._label_set_pos = None
        self._cur_stack_size = None
        self._max_stack_size = None

    def execute(self, **ctx):
        """
        Execute the stub
        """
        exec self._code in ctx

        return ctx[const.Stub.RET_VARNAME]

    @contextlib.contextmanager
    def stack_size(self, size):
        if size > 0:
            self._inc_stack_size(size)

        try:
            yield
        finally:
            if size > 0:
                self._dec_stack_size(size)

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
        Get packed code
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        return self._code

    def set_label(self, label):
        """
        set current position as lable position
        """
        if label not in self._label_set_pos:
            raise ValueError("wrong label: " + label)

        self._label_set_pos[label][-1] = self._cur_pos

    def require_label(self, label):
        """
        require a new label to be set
        """
        if label not in self._label_set_pos:
            self._label_set_pos[label] = []
            self._label_invoke_pos[label] = []

        self._label_set_pos[label].append(-1)

    # ~ bytecode invoking helpers
    @invoke
    def invoke_load_const(self, const):
        self._inc_stack_size()
        idx = self._get_constant_index_or_store(const)
        return self._invoke_load_const_by_idx(idx)

    @invoke
    def invoke_binary_add(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_ADD"])

    @invoke
    def invoke_binary_subtract(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_SUBTRACT"])

    @invoke
    def invoke_binary_multiple(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_MULTIPLY"])

    @invoke
    def invoke_binary_divide(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_DIVIDE"])

    @invoke
    def invoke_binary_modulo(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_MODULO"])

    @invoke
    def invoke_binary_and(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_AND"])

    @invoke
    def invoke_binary_power(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_POWER"])

    @invoke
    def invoke_binary_rshift(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["BINARY_RSHIFT"])

    @invoke
    def invoke_print_item(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["PRINT_ITEM"])

    @invoke
    def invoke_print_newline(self):
        return struct.pack("B", opmap["PRINT_NEWLINE"])

    @invoke
    def invoke_return_value(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["RETURN_VALUE"])

    @invoke
    def invoke_unary_negative(self):
        return struct.pack("B", opmap["UNARY_NEGATIVE"])

    @invoke
    def invoke_unary_positive(self):
        return struct.pack("B", opmap["UNARY_POSITIVE"])

    @invoke
    def invoke_store_fast(self, var_name):
        self._dec_stack_size()
        idx = self._get_local_variable_index_or_store(var_name)
        return self._invoke_store_fast_by_idx(idx)

    @invoke
    def invoke_load_fast(self, var_name):
        self._inc_stack_size()
        idx = self._get_local_variable_index_or_store(var_name)
        return (
            struct.pack("B", opmap["LOAD_FAST"]),
            struct.pack("H", idx))

    @invoke
    def invoke_store_global(self, var_name):
        self._dec_stack_size()
        idx = self._get_global_variable_index_or_store(var_name)

        return (
            struct.pack("B", opmap["STORE_GLOBAL"]),
            struct.pack("H", idx))

    @invoke
    def invoke_load_global(self, var_name):
        self._inc_stack_size()
        idx = self._get_global_variable_index_or_store(var_name)
        return self._invoke_load_global_by_idx(idx)

    @invoke
    def invoke_nop(self):
        return struct.pack("B", opmap["NOP"])

    @invoke
    def invoke_pop_top(self):
        self._dec_stack_size()
        return struct.pack("B", opmap["POP_TOP"])

    @invoke
    def invoke_jump_absolute(self, label):
        self._invoke_label(label, self._cur_pos + 1)
        return (
            struct.pack("B", opmap["JUMP_ABSOLUTE"]),
            struct.pack("H", 0))

    @invoke
    def invoke_pop_jump_if_false(self, label):
        self._invoke_label(label, self._cur_pos + 1)
        return (
            struct.pack("B", opmap["POP_JUMP_IF_FALSE"]),
            struct.pack("H", 0))

    @invoke
    def invoke_pop_jump_if_true(self, label):
        self._invoke_label(label, self._cur_pos + 1)
        return (
            struct.pack("B", opmap["POP_JUMP_IF_TRUE"]),
            struct.pack("H", 0))

    @invoke
    def invoke_jump_if_true_or_pop(self, label):
        self._invoke_label(label, self._cur_pos + 1)
        return (
            struct.pack("B", opmap["JUMP_IF_TRUE_OR_POP"]),
            struct.pack("H", 0))

    @invoke
    def invoke_dup_top(self):
        self._inc_stack_size()
        return struct.pack("B", opmap["DUP_TOP"])

    @invoke
    def invoke_rot(self, n):
        if n == 2:
            return struct.pack("B", opmap["ROT_TWO"])
        elif n == 3:
            return struct.pack("B", opmap["ROT_THREE"])
        elif n == 4:
            return struct.pack("B", opmap["ROT_FOUR"])
        else:
            raise ValueError("can only rotate 2, 3 or 4 values")

    @invoke
    def invoke_compare_op(self, op):
        self._dec_stack_size()
        return (
            struct.pack("B", opmap["COMPARE_OP"]),
            struct.pack("H", cmp_op.index(op)))

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

    def _invoke_label(self, label, replace_pos):
        if label not in self._label_set_pos:
            raise ValueError("wrong label: " + label)

        pos = self._label_invoke_pos[label]
        while len(pos) < len(self._label_set_pos[label]):
            pos.append([])

        pos[-1].append(replace_pos)

    def _inc_stack_size(self, sz=1):
        self._cur_stack_size += sz
        if self._cur_stack_size > self._max_stack_size:
            self._max_stack_size = self._cur_stack_size

    def _dec_stack_size(self, sz=1):
        self._cur_stack_size -= sz
