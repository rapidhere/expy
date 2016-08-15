#-*- coding: utf-8 -*-
"""
Functions

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"
__all__ = ["invoke_function"]

from expy.exception import NoSuchFunction


func_map = {}


def invoke_function(func_name, stub):
    """
    invoke a function call into stub
    """
    try:
        func_map[func_name](stub)
    except KeyError:
        raise NoSuchFunction(func_name)


# dec, register a function as expy function
def expy_func(f):
    func_map[f.__name__] = f
    return f


#~ functions goes here

@expy_func
def add(stub):
    stub.invoke_binary_add()


@expy_func
def sub(stub):
    stub.invoke_binary_subtract()
