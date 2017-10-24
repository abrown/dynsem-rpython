from src.meta.e2 import e2
from src.meta.interpreter import Interpreter
from src.meta.parser import Parser


def main(argv):
    program = Parser.term("""
    block([
      assign(a, 0),
      while(leq(retrieve(a), 10),
        block([
          assign(a, add(retrieve(a), 1)), 
          write(retrieve(a))
        ])
      )
    ])
    """)
    Interpreter(1).interpret(e2, program)
    return 0


if __name__ == "__main__":
    main([])


def target(*args):
    return main, None
