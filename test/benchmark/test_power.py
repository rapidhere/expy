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

from expy import Compiler


def run_single(stub, exp):
    start = time.time() * 1000
    r0 = stub.execute()
    cur0 = time.time() * 1000 - start

    start = time.time() * 1000
    r1 = eval(exp)
    cur1 = time.time() * 1000 - start

    assert r0 == r1
    return cur0, cur1


def run(desc, expy_exp, exp, n):
    sum0, sum1 = 0, 0
    comp = Compiler()
    stub = comp.compile(expy_exp)

    for i in xrange(n):
        cur0, cur1 = run_single(stub, exp)
        sum0 += cur0
        sum1 += cur1

    ret0, ret1 = float(sum0) / float(n), float(sum1) / float(n)

    print ">>> benchmark on: %s" % desc
    print "    expy: %.5fms eval: %.5fms" % (ret0, ret1)
    print


if __name__ == "__main__":
    run(
        "long multiply",
        "*".join([str(x) for x in range(100)]),
        "*".join([str(x) for x in range(100)]),
        10000)

    run(
        "large power",
        "power(7, 200000)",
        "7 ** 200000",
        50)
