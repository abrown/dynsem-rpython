import unittest

from src.meta.interpreter import Interpreter
from src.meta.parser import Parser
from src.meta.e2 import e2
from src.meta.term import ApplTerm


class TestE2(unittest.TestCase):
    def test_if(self):
        term = Parser.term("ifz(leq(2, 1), a(), b())")

        result = Interpreter().interpret(e2, term)

        self.assertEqual(result, ApplTerm("b"))

    def test_block_environment(self):
        term = Parser.term("block([assign(a, 1), write(retrieve(a))])")

        result = Interpreter().interpret(e2, term)

        self.assertEqual(result, ApplTerm("block"))
        self.assertEqual(len(result.args), 0)

    def test_while(self):
        term = Parser.term("block(["
                           "assign(a, 0),"
                           "while("
                            "leq(retrieve(a), 10), "
                            "block([assign(a, add(retrieve(a), 1)), write(retrieve(a))])"
                           ")])")

        result = Interpreter().interpret(e2, term)

        self.assertEqual(result, ApplTerm("block"))
        self.assertEqual(len(result.args), 0)


if __name__ == '__main__':
    unittest.main()
