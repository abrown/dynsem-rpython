import unittest

from ..dynsem import *
from ..interpreter import Interpreter
from ..parser import Parser


class TestInterpreter(unittest.TestCase):
    def test_one_transformation(self):
        mod = Module()
        mod.rules.append(Rule(Parser.term("a(x)"), Parser.term("b"), [Parser.premise("x == 1")]))
        term = Parser.term("a(1)")

        result = Interpreter.interpret(mod, term)

        self.assertEqual(result, Parser.term("b"))

    def test_multiple_transformations(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b()"))
        mod.rules.append(Parser.rule("b() --> c()"))
        mod.rules.append(Parser.rule("c() --> d()"))
        term = Parser.term("a()")

        result = Interpreter.interpret(mod, term)

        self.assertEqual(result, Parser.term("d()"))


if __name__ == '__main__':
    unittest.main()
