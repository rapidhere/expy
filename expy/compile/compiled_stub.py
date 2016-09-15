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
def invoke(stacksize, const_var=False, global_var=False, fast_var=False, lable=False, cmp_oper=False):
    def _dec(f):
        def _f(self, *inargs):
            # calc args
            args = []
            if const_var:
                args.append(self._get_constant_index_or_store(inargs[0]))
            elif global_var:
                args.append(self._get_global_variable_index_or_store(inargs[0]))
            elif fast_var:
                args.append(self._get_local_variable_index_or_store(inargs[0]))
            elif lable:
                args.append(inargs[0])
            elif cmp_oper:
                args.append(cmp_op.index(inargs[0]))
            else:
                args = inargs

            # calc stack size
            self._inc_stack_size(stacksize)

            # invoke bytecode
            for b in f(self, *args):
                append_byte(self._bytecodes, b)
                self._cur_pos += len(b)

            # channing
            return self

        _f.__name__ = f.__name__
        return _f

    return _dec


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

            # needn't to calculate stack size
            for c in self._invoke_load_global_by_idx(gi):
                append_byte(precode, c)

            for c in self._invoke_store_fast_by_idx(li):
                append_byte(precode, c)

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
        (self.invoke_store_global(const.Stub.RET_VARNAME)
            .invoke_load_const(None)
            .invoke_return_value())

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
                self._inc_stack_size(-size)

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

    def disassemble(self):
        """
        dump the code packed code object
        """
        if self._code is None:
            raise RuntimeError("Please pack the code object first")

        print "byte code disassamble Info: "
        print " # filename: " + self.code.co_filename
        print " # module: " + self.code.co_name
        print " # stacksize: " + str(self.code.co_stacksize)
        print " # consts: " + ", ".join([str(x) for x in self.code.co_consts])
        print " # number of vars: " + str(self.code.co_nlocals)
        print " # variables: " + ", ".join([str(x) for x in self.code.co_varnames])
        print " # globals: " + ", ".join([str(x) for x in self.code.co_names])
        print "code: "
        dis.dis(self._code)
        print

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
        return self

    def require_label(self, label):
        """
        require a new label to be set
        """
        if label not in self._label_set_pos:
            self._label_set_pos[label] = []
            self._label_invoke_pos[label] = []

        self._label_set_pos[label].append(-1)
        return self

    # ~ bytecode invoking helpers
    @invoke(stacksize=1, const_var=True)
    def invoke_load_const(self, idx):
        return self._invoke_load_const_by_idx(idx)

    @invoke(stacksize=-1)
    def invoke_binary_add(self):
        yield struct.pack("B", opmap["BINARY_ADD"])

    @invoke(stacksize=-1)
    def invoke_binary_subtract(self):
        yield struct.pack("B", opmap["BINARY_SUBTRACT"])

    @invoke(stacksize=-1)
    def invoke_binary_multiple(self):
        yield struct.pack("B", opmap["BINARY_MULTIPLY"])

    @invoke(stacksize=-1)
    def invoke_binary_divide(self):
        yield struct.pack("B", opmap["BINARY_DIVIDE"])

    @invoke(stacksize=-1)
    def invoke_binary_modulo(self):
        yield struct.pack("B", opmap["BINARY_MODULO"])

    @invoke(stacksize=-1)
    def invoke_binary_and(self):
        yield struct.pack("B", opmap["BINARY_AND"])

    @invoke(stacksize=-1)
    def invoke_binary_power(self):
        yield struct.pack("B", opmap["BINARY_POWER"])

    @invoke(stacksize=-1)
    def invoke_binary_rshift(self):
        yield struct.pack("B", opmap["BINARY_RSHIFT"])

    @invoke(stacksize=-1)
    def invoke_print_item(self):
        return struct.pack("B", opmap["PRINT_ITEM"])

    @invoke(stacksize=0)
    def invoke_print_newline(self):
        yield struct.pack("B", opmap["PRINT_NEWLINE"])

    @invoke(stacksize=-1)
    def invoke_return_value(self):
        yield struct.pack("B", opmap["RETURN_VALUE"])

    @invoke(stacksize=0)
    def invoke_unary_negative(self):
        yield struct.pack("B", opmap["UNARY_NEGATIVE"])

    @invoke(stacksize=0)
    def invoke_unary_positive(self):
        yield struct.pack("B", opmap["UNARY_POSITIVE"])

    @invoke(stacksize=-1, fast_var=True)
    def invoke_store_fast(self, idx):
        return self._invoke_store_fast_by_idx(idx)

    @invoke(stacksize=1, fast_var=True)
    def invoke_load_fast(self, idx):
        yield struct.pack("B", opmap["LOAD_FAST"])
        yield struct.pack("H", idx)

    @invoke(stacksize=-1, global_var=True)
    def invoke_store_global(self, idx):
        yield struct.pack("B", opmap["STORE_GLOBAL"]),
        yield struct.pack("H", idx)

    @invoke(stacksize=1, global_var=True)
    def invoke_load_global(self, idx):
        return self._invoke_load_global_by_idx(idx)

    @invoke(stacksize=0)
    def invoke_nop(self):
        yield struct.pack("B", opmap["NOP"])

    @invoke(stacksize=-1)
    def invoke_pop_top(self):
        yield struct.pack("B", opmap["POP_TOP"])

    @invoke(stacksize=0, lable=True)
    def invoke_jump_absolute(self, label):
        yield struct.pack("B", opmap["JUMP_ABSOLUTE"])
        yield self._invoke_label(label, self._cur_pos)

    @invoke(stacksize=-1, lable=True)
    def invoke_pop_jump_if_false(self, label):
        yield struct.pack("B", opmap["POP_JUMP_IF_FALSE"])
        yield self._invoke_label(label, self._cur_pos)

    @invoke(stacksize=-1, lable=True)
    def invoke_pop_jump_if_true(self, label):
        yield struct.pack("B", opmap["POP_JUMP_IF_TRUE"])
        yield self._invoke_label(label, self._cur_pos)

    @invoke(stacksize=-1, lable=True)
    def invoke_jump_if_true_or_pop(self, label):
        yield struct.pack("B", opmap["JUMP_IF_TRUE_OR_POP"])
        yield self._invoke_label(label, self._cur_pos)

    @invoke(stacksize=1)
    def invoke_dup_top(self):
        yield struct.pack("B", opmap["DUP_TOP"])

    @invoke(stacksize=0)
    def invoke_rot(self, n):
        if n == 2:
            yield struct.pack("B", opmap["ROT_TWO"])
        elif n == 3:
            yield struct.pack("B", opmap["ROT_THREE"])
        elif n == 4:
            yield struct.pack("B", opmap["ROT_FOUR"])
        else:
            raise ValueError("can only rotate 2, 3 or 4 values")

    @invoke(stacksize=-1, cmp_oper=True)
    def invoke_compare_op(self, op):
        yield struct.pack("B", opmap["COMPARE_OP"])
        yield struct.pack("H", op)

    # ~ other helpers
    def _gen_code(self, *args):
        # a trick to get code object
        def __useless():
            return
        return type(__useless.__code__)(*args)

    def _invoke_load_const_by_idx(self, idx):
        yield struct.pack("B", opmap["LOAD_CONST"])
        yield struct.pack("H", idx)

    def _invoke_load_global_by_idx(self, idx):
        yield struct.pack("B", opmap["LOAD_GLOBAL"])
        yield struct.pack("H", idx)

    def _invoke_store_fast_by_idx(self, idx):
        yield struct.pack("B", opmap["STORE_FAST"])
        yield struct.pack("H", idx)

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

        return struct.pack("H", 0)

    def _inc_stack_size(self, sz=1):
        self._cur_stack_size += sz
        if self._cur_stack_size > self._max_stack_size:
            self._max_stack_size = self._cur_stack_size
