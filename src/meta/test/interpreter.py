import unittest

from src.meta.dynsem import Module, Rule
from src.meta.interpreter import Interpreter, InterpreterError
from src.meta.parser import Parser
from src.meta.term import IntTerm, EnvWriteTerm, ApplTerm


class TestInterpreter(unittest.TestCase):
    def test_one_transformation(self):
        mod = Module()
        mod.rules.append(Rule(Parser.term("a(x)"), Parser.term("b"), [Parser.premise("x == 1")]))
        term = Parser.term("a(1)")

        result = Interpreter().interpret(mod, term)

        self.assertEqual(result, Parser.term("b"))

    def test_multiple_transformations(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b()"))
        mod.rules.append(Parser.rule("b() --> c()"))
        mod.rules.append(Parser.rule("c() --> d()"))
        term = Parser.term("a()")

        result = Interpreter().interpret(mod, term)

        self.assertEqual(result, Parser.term("d()"))

    def test_invalid_premise(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b() where 1 == 2"))
        term = Parser.term("a()")

        with self.assertRaises(InterpreterError):
            Interpreter().interpret(mod, term)  # does not know where to go when 1 != 2

    def test_transformation_of_result(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b where b => 2"))
        term = Parser.term("a()")

        result = Interpreter().interpret(mod, term)  # does not know where to go when 1 != 2

        self.assertEqual(result, IntTerm(2))

    def test_environment_assignment(self):
        mod = Module()
        mod.rules.append(Parser.rule("E |- bindVar(x, v) --> {x |--> v, E}"))
        term = Parser.term("bindVar(x, 1)")
        sut = Interpreter()

        result = sut.interpret(mod, term)

        self.assertIsInstance(result, EnvWriteTerm)
        self.assertEqual(IntTerm(1), sut.environment["x"])

    def test_environment_retrieval(self):
        mod = Module()
        mod.rules.append(Parser.rule("E |- read(y) --> E[y]"))
        term = Parser.term("read(y)")
        sut = Interpreter()
        sut.environment["y"] = 42

        result = sut.interpret(mod, term)

        self.assertEqual(result, 42)

    def test_reduction_premise(self):
        mod = Module()
        mod.rules.append(Parser.rule("b() --> c()"))
        mod.rules.append(Parser.rule("a(x) --> y where x --> y"))
        term = Parser.term("a(b())")

        result = Interpreter().interpret(mod, term)

        self.assertEqual(result, ApplTerm("c"))

        # def test_assignment_then_reading(self):
        #     mod = Module()
        #     mod.rules.append(Parser.rule("E |- write(x, v) --> {x |--> v, E}"))
        #     mod.rules.append(Parser.rule("E |- read(x) --> E[x]"))
        #     term = Parser.term("bindVar(x, 1); read(x)") # TODO no way to do sequences currently
        #     sut = Interpreter()
        #
        #     out = sut.interpret(mod, term)
        #
        #     self.assertIsInstance(out, EnvTerm)
        #     self.assertEqual(IntTerm(1), sut.environment["x"])


if __name__ == '__main__':
    unittest.main()
