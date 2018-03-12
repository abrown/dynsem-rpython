import os
import sys

from src.compile.handmade import Interpreter
from src.meta.parser import Parser


def read_fd(fd):
    """Read a file handle to completion"""
    text = ""
    while True:
        read = os.read(fd, 4096)
        if len(read) == 0:
            break
        text += read
    return text


def read_file(filename):
    """Read a file"""
    fd = os.open(filename, os.O_RDONLY, 0o777)
    text = read_fd(fd)
    os.close(fd)
    return text


def main(argv):
    """Parse and run any E2 program"""
    # parse input program
    program_contents = read_file(argv[1]) if len(argv) > 1 else read_fd(0)  # rpython barfs with sys.stdin
    program = Parser.term(program_contents)

    # set debug level
    debug_level = 0
    try:
        debug_level = int(os.environ['DEBUG'])
    except KeyError:
        # there may be a better way to do this but RPython apparently does not allow "'DEBUG' in os.environ"
        pass

    # run the program
    Interpreter(debug_level).interpret(program)

    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None
