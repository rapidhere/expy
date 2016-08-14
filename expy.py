"""
A fast python expression executor

Author: rapidhere@gmail.com
"""
import argparse
import dis

from expy import Compiler
from expy.exception import ExpyCompilingError


def run():
    parser = argparse.ArgumentParser(
        prog="expy",
        description="a fast python expression executor",
        epilog="author & maintainer: rapidhere@gmail.com")

    parser.add_argument(
        "expression", type=str,
        help="the expression to execute")

    parser.add_argument(
        "-v", "--version", action="version",
        help="print the version and exit",
        version="expy v0.1")

    parser.add_argument(
        "--print-dis", action="store_true",
        help="print the code object disassamble info for debug usage",
        default=False)

    parser.add_argument(
        "--disable-print", action="store_true",
        help="disable auto print when executing",
        default=False)

    args = parser.parse_args()
    compiler = Compiler()

    try:
        stub = compiler.compile(
            args.expression,
            pack_print=not args.disable_print)
    except ExpyCompilingError as e:
        print "compiling failed: "
        print "    " + str(e)
        exit(1)

    if args.print_dis:
        print "byte codeDisassamble Info: "
        dis.dis(stub.code)
        print

    print "execute `%s`\n" % args.expression
    stub.execute()


if __name__ == "__main__":
    run()
