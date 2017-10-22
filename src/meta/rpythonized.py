from dynsem import Module
from interpreter import Interpreter
from parser import Parser


def main(argv):
    mod = Module()
    mod.rules.append(Parser.rule("a() --> b()"))
    mod.rules.append(Parser.rule("b() --> c()"))
    mod.rules.append(Parser.rule("c() --> d()"))

    term = Parser.term("a()")

    Interpreter().interpret(mod, term, True)
    return 0


if __name__ == "__main__":
    main([])


def target(*args):
    return main, None
