# -*- coding: utf-8 -*-
"""
test the benchmark of power

Author: rapidhere@gmail.com
"""
__author__ = "rapidhere@gmail.com"

import os
import sys

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..", "..")))

import time
from py_expression_eval import Parser
from simpleeval import simple_eval
from asteval import Interpreter

from expy import Compiler


def run_single(stub, exp, pyeval, sexp, astexp):
    start = time.time() * 1000
    stub.execute()
    cur0 = time.time() * 1000 - start

    start = time.time() * 1000
    eval(exp)
    cur1 = time.time() * 1000 - start

    start = time.time() * 1000
    pyeval.evaluate({})
    cur2 = time.time() * 1000 - start

    start = time.time() * 1000
    simple_eval(sexp)
    cur3 = time.time() * 1000 - start

    inter = Interpreter()
    start = time.time() * 1000
    inter(astexp)
    cur4 = time.time() * 1000 - start

    return cur0, cur1, cur2, cur3, cur4


def run(desc, expy_exp, exp, pyeval_exp, sexp, astexp, n):
    sum0, sum1, sum2, sum3, sum4 = 0, 0, 0, 0, 0
    comp = Compiler()
    stub = comp.compile(expy_exp)
    pyeval = Parser().parse(pyeval_exp)

    for i in xrange(n):
        cur0, cur1, cur2, cur3, cur4 = run_single(stub, exp, pyeval, sexp, astexp)
        sum0 += cur0
        sum1 += cur1
        sum2 += cur2
        sum3 += cur3
        sum4 += cur4

    ret0, ret1, ret2, ret3, ret4 = (
        float(sum0) / float(n),
        float(sum1) / float(n),
        float(sum2) / float(n),
        float(sum3) / float(n),
        float(sum4) / float(n))

    print ">>> benchmark on: %s" % desc
    print "expy: %.5fms\neval: %.5fms\npy_expression_eval: %.5fms\nsimpeeval: %.5fms\nasteval: %.5fms" % (
        ret0, ret1, ret2, ret3, ret4)
    print


if __name__ == "__main__":
    run(
        "long multiply",
        "*".join([str(x) for x in range(20)]),
        "*".join([str(x) for x in range(20)]),
        "*".join([str(x) for x in range(20)]),
        "*".join([str(x) for x in range(20)]),
        "*".join([str(x) for x in range(20)]),
        10000)

    run(
        "large power",
        "power(7, 200000)",
        "7 ** 200000",
        "7 ^ 20",           # not availabel
        "7 ** 200000",
        "7 ** 20",
        20)
