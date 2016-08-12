#-*- coding: utf-8 -*-

__author__ = "rapidhere"

import os
import sys

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..")))

import unittest

from ast.test_automation import TestNFA


def load():
    return (
        TestNFA.load_cases())


def run():
    ts = unittest.TestSuite()
    ts.addTests(load())

    tr = unittest.TextTestRunner()
    ret = tr.run(ts)
    return ret.wasSuccessful()


if __name__ == "__main__":
    if run():
        exit(0)
    else:
        exit(1)
