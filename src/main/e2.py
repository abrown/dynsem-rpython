import os
import sys

from src.meta.e2 import e2
from src.meta.interpreter import Interpreter
from src.meta.parser import Parser


def read_file(filename):
    fd = os.open(filename, os.O_RDONLY, 0o777)
    text = ""

    while True:
        read = os.read(fd, 4096)
        if len(read) == 0:
            break
        text += read

    os.close(fd)
    return text


def main(argv):
    """Parse and run any E2 program"""

    try:
        file = argv[1]
    except IndexError:
        raise RuntimeError("Expect one file name argument passed, e.g. ./e2 program.e2")

    program_contents = read_file(argv[1])
    program = Parser.term(program_contents)

    Interpreter(e2).interpret(program)
    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None
