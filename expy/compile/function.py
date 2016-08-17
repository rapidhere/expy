#-*- coding: utf-8 -*-
"""
Functions

Author: rapidhere@gmail.com
"""
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

        if f[const.Function.FUNCMAP_KEY_ARGLEN] != len(args):
            raise FunctionArgumentsLengthError(
                func_name, f[const.Function.FUNCMAP_KEY_ARGLEN], len(args))

        f[const.Function.FUNCMAP_KEY_FUNC](stub)
    except KeyError:
        raise NoSuchFunction(func_name)


# dec, register a function as expy function
def expy_func(arg_len):
    def _dec(f):
        func_map[f.__name__] = {
            const.Function.FUNCMAP_KEY_FUNC: f,
            const.Function.FUNCMAP_KEY_ARGLEN: arg_len}
        return f

    return _dec


#~ functions goes here

@expy_func(2)
def add(stub):
    stub.invoke_binary_add()


@expy_func(2)
def sub(stub):
    stub.invoke_binary_subtract()
