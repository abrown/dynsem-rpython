import os
import sys

from src.compile.handmade import Interpreter
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

    # parse input program
    try:
        file = argv[1]
    except IndexError:
        print("Expected one file name argument to be passed, e.g. ./e2 program.e2")
        raise RuntimeError
    program_contents = read_file(argv[1])
    program = Parser.term(program_contents)

    # set debug level
    debug_level = 0
    try:
        debug_level = int(os.environ['DEBUG'])
    except KeyError:
        # there may be a better way to do this but RPython apparently does not allow "'DEBUG' in os.environ"
        pass

    # run the program
    result = Interpreter(debug_level).interpret(program)
    print(result.to_string())

    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None
