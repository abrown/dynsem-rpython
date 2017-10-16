import unittest

from meta.dynsem import *
from meta.interpreter import Interpreter
from meta.parser import Parser


class TestInterpreter(unittest.TestCase):
    def test_header(self):
        mod = Module()
        mod.rules.append(Rule(Parser.term("a(x)"), Parser.term("b"), [Parser.premise("x == 1")]))
        term = Parser.term("a(1)")

        result = Interpreter.interpret(mod, term)

        self.assertEqual(result, Parser.term("b"))


if __name__ == '__main__':
    unittest.main()
