# -*- coding: utf-8 -*-
"""
Functions

Author: rapidhere@gmail.com
"""
# flake8: noqa
__author__ = "rapidhere@gmail.com"
__all__ = ["check_and_invoke_function"]

from expy.exception import NoSuchFunction, FunctionArgumentsLengthError
from expy import const


func_map = {}


def check_and_invoke_function(func_name, args, stub):
    """
    check a function, and invoke it
    """
    try:
        f = func_map[func_name]

        if f.expy_arglen != len(args):
            raise FunctionArgumentsLengthError(
                func_name, f.expy_arglen, len(args))

        with stub.stack_size(f.expy_stacksize):
            f(stub)
    except KeyError:
        raise NoSuchFunction(func_name)


# dec, register a function as expy function
def expy_func(arg_len, description, stack_size=-1):
    """
    when stacksize set to -1, means stacksize is auto discovered, otherwise is specified
    """
    def _dec(f):
        func_map[f.__name__] = f

        f.expy_description = description
        f.expy_arglen = arg_len
        f.expy_stacksize = stack_size
        return f

    return _dec


#~ functions goes here

@expy_func(2, "calculate a + b")
def add(stub):
    stub.invoke_binary_add()


@expy_func(2, "calculate a - b")
def sub(stub):
    stub.invoke_binary_subtract()


@expy_func(1, "just return a, do nothing")
def nop(stub):
    stub.invoke_nop()


@expy_func(
    arg_len=2, stack_size=64,
    description="calculate a ^ b, note 0 ^ 0 = 1. must be integers, and b must be positive")
def power(stub):
    # NOTE: mark 0 ** 0 = 1, same as python's default behaviour
    # TODO: only available for integer indexes
    # TODO: assert n >= 0
    # n is always on the top of stack

    # stub begin
    (stub

    # we need these labels in this scope:
    .require_label(const.Function.POWER_N_LOOP_LABEL)
    .require_label(const.Function.POWER_C_LOOP_LABEL)
    .require_label(const.Function.POWER_END_LABEL)

    # store a
    .invoke_rot(2)
    .invoke_store_fast(const.Function.POWER_A_VARNAME)

    # ~ first: push n bits into stac
    # insert a end bit, -1
    .invoke_load_const(-1)
    .invoke_rot(2)

    # label: __n_while_start
    .set_label(const.Function.POWER_N_LOOP_LABEL)
    # push n & 1 on stack
    .invoke_dup_top()
    .invoke_load_const(1)
    .invoke_binary_and()

    # n = n >> 1
    .invoke_rot(2)
    .invoke_load_const(1)
    .invoke_binary_rshift()

    # if n == 0, end loop
    .invoke_jump_if_true_or_pop(const.Function.POWER_N_LOOP_LABEL)

    # ~ second: calc result
    # u = 1
    .invoke_load_const(1)

    # label: __c_while_start
    .set_label(const.Function.POWER_C_LOOP_LABEL)

    # if bit < 0, end loop
    .invoke_rot(2)
    .invoke_dup_top()
    .invoke_load_const(0)
    .invoke_compare_op("<")
    .invoke_pop_jump_if_true(const.Function.POWER_END_LABEL)
    .invoke_rot(2)

    # u = u * u
    .invoke_dup_top()
    .invoke_binary_multiple()

    # put bit to the top
    .invoke_rot(2)

    # if bit == 0, next loop
    .invoke_pop_jump_if_false(const.Function.POWER_C_LOOP_LABEL)

    # if bit == 1, multiply by a
    .invoke_load_fast(const.Function.POWER_A_VARNAME)
    .invoke_binary_multiple()
    .invoke_jump_absolute(const.Function.POWER_C_LOOP_LABEL)

    # label: __end
    .set_label(const.Function.POWER_END_LABEL)
    # pop top -1
    .invoke_pop_top()

    # end stub
    )


@expy_func(
    arg_len=3, stack_size=64,
    description="calculate a ^ b % c, all must be integers, and b, c must be positive")
def powermod(stub):
    # NOTE: see @func expy_func
    # args a, n, m
    # n is always on the top of stack

    # stub begin
    (stub

    # we need these labels in this scope:
    .require_label(const.Function.POWERMOD_N_LOOP_LABEL)
    .require_label(const.Function.POWERMOD_C_LOOP_LABEL)
    .require_label(const.Function.POWERMOD_END_LABEL)

    # store m
    .invoke_store_fast(const.Function.POWERMOD_M_VARNAME)

    # store a mod m
    .invoke_rot(2)
    .invoke_load_fast(const.Function.POWERMOD_M_VARNAME)
    .invoke_binary_modulo()
    .invoke_store_fast(const.Function.POWERMOD_A_VARNAME)

    # ~ first: push n bits into stac
    # insert a end bit, -1
    .invoke_load_const(-1)
    .invoke_rot(2)

    # label: __n_while_start
    .set_label(const.Function.POWERMOD_N_LOOP_LABEL)
    # push n & 1 on stack
    .invoke_dup_top()
    .invoke_load_const(1)
    .invoke_binary_and()

    # n = n >> 1
    .invoke_rot(2)
    .invoke_load_const(1)
    .invoke_binary_rshift()

    # if n == 0, end loop
    .invoke_jump_if_true_or_pop(const.Function.POWERMOD_N_LOOP_LABEL)

    # ~ second: calc result
    # u = 1
    .invoke_load_const(1)

    # label: __c_while_start
    .set_label(const.Function.POWERMOD_C_LOOP_LABEL)

    # if bit < 0, end loop
    .invoke_rot(2)
    .invoke_dup_top()
    .invoke_load_const(0)
    .invoke_compare_op("<")
    .invoke_pop_jump_if_true(const.Function.POWERMOD_END_LABEL)
    .invoke_rot(2)

    # u = u * u modulo m
    .invoke_dup_top()
    .invoke_binary_multiple()
    .invoke_load_fast(const.Function.POWERMOD_M_VARNAME)
    .invoke_binary_modulo()

    # put bit to the top
    .invoke_rot(2)

    # if bit == 0, next loop
    .invoke_pop_jump_if_false(const.Function.POWERMOD_C_LOOP_LABEL)

    # if bit == 1, multiply by a
    .invoke_load_fast(const.Function.POWERMOD_A_VARNAME)
    .invoke_binary_multiple()
    .invoke_load_fast(const.Function.POWERMOD_M_VARNAME)
    .invoke_binary_modulo()
    .invoke_jump_absolute(const.Function.POWERMOD_C_LOOP_LABEL)

    # label: __end
    .set_label(const.Function.POWERMOD_END_LABEL)
    # pop top -1
    .invoke_pop_top()

    # end stub
    )
