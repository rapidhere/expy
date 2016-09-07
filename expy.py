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
        "--variables",
        help="set variables, etc a=1,b=2",
        default="")

    parser.add_argument(
        "--print-dis", action="store_true",
        help="print the code object disassamble info for debug usage",
        default=False)

    parser.add_argument(
        "--stack-size", help="specify the stack-size of the stubs",
        type=int,
        default=-1)

    parser.add_argument(
        "--disable-print", action="store_true",
        help="disable auto print when executing",
        default=False)

    args = parser.parse_args()
    compiler = Compiler()

    try:
        stub = compiler.compile(
            args.expression,
            stacksize=args.stack_size)
    except ExpyCompilingError as e:
        print "compiling failed: "
        print "    " + str(e)
        exit(1)

    if args.print_dis:
        print "byte code disassamble Info: "
        dis.dis(stub.code)
        print
    try:
        variables = get_variables(args)
    except ValueError as e:
        print "variable syntax error: " + e.message
        exit(-1)

    print "variables:"
    for k, v in variables.items():
        print "  %s = %s" % (str(k), str(v))
    print

    print "execute `%s`\n" % args.expression
    result = stub.execute(**variables)

    if not args.disable_print:
        print "  > " + str(result)


def get_variables(args):
    ret = {}

    for exp in args.variables.strip().split(","):
        if not exp:
            continue

        key, val = exp.split("=")

        if "." in val:
            ret[key] = float(val)
        else:
            ret[key] = int(val)

    return ret


if __name__ == "__main__":
    run()
