import unittest

from src.meta.dynsem import Module, NativeFunction, DynsemError
from src.meta.interpreter import Interpreter
from src.meta.parser import Parser
from src.meta.term import IntTerm, MapWriteTerm, ApplTerm, VarTerm


class TestInterpreter(unittest.TestCase):
    def test_one_transformation(self):
        mod = Module()
        mod.rules.append(Parser.rule("a(x) --> b where x == 1"))
        term = Parser.term("a(1)")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, VarTerm("b"))

    def test_multiple_transformations(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b()"))
        mod.rules.append(Parser.rule("b() --> c()"))
        mod.rules.append(Parser.rule("c() --> d()"))
        term = Parser.term("a()")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, Parser.term("d()"))

    def test_invalid_premise(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b() where 1 == 2"))
        term = Parser.term("a()")

        with self.assertRaises(DynsemError):
            Interpreter(mod).interpret(term)  # does not know where to go when 1 != 2

    def test_transformation_of_result(self):
        mod = Module()
        mod.rules.append(Parser.rule("a() --> b where b => 2"))
        term = Parser.term("a()")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, IntTerm(2))

    def test_environment_assignment(self):
        mod = Module()
        mod.rules.append(Parser.rule("E |- bindVar(k, v) --> {k |--> v, E}"))
        term = Parser.term("bindVar(a, 1)")
        sut = Interpreter(mod)
        sut.environment = {'a': IntTerm(42)}  # this should be overwritten

        result = sut.interpret(term)

        self.assertIsInstance(result, MapWriteTerm)
        self.assertEqual(IntTerm(1), sut.environment["a"])

    def test_environment_retrieval(self):
        mod = Module()
        mod.rules.append(Parser.rule("E |- read(y) --> E[y]"))
        term = Parser.term("read(y)")
        sut = Interpreter(mod)
        sut.environment["y"] = 42

        result = sut.interpret(term)

        self.assertEqual(result, 42)

    def test_reduction_premise(self):
        mod = Module()
        mod.rules.append(Parser.rule("b() --> c()"))
        mod.rules.append(Parser.rule("a(x) --> y where x --> y"))
        term = Parser.term("a(b())")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, ApplTerm("c"))

    def test_block(self):
        mod = Module()
        mod.rules.append(Parser.rule("block([x | xs]) --> block(xs)"))
        term = Parser.term("block([1, 2, 3, 4])")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, ApplTerm("block"))

    def test_native(self):
        mod = Module()
        mod.rules.append(Parser.rule("a(x) --> add(x, 1)"))
        mod.native_functions.append(NativeFunction(Parser.term("add(x, y)"), lambda x, y: x + y))
        term = Parser.term("a(1)")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, IntTerm(2))


if __name__ == '__main__':
    unittest.main()
