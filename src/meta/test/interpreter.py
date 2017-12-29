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
        a = sut.environment.locate_and_put("a", IntTerm(42))  # this should be overwritten

        result = sut.interpret(term)

        self.assertIsInstance(result, MapWriteTerm)
        self.assertEqual(IntTerm(1), sut.environment.get(a))

    def test_environment_retrieval(self):
        mod = Module()
        mod.rules.append(Parser.rule("E |- read(y) --> E[y]"))
        term = Parser.term("read(y)")
        sut = Interpreter(mod)
        sut.environment.locate_and_put("y", 42)

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
        mod.native_functions.append(NativeFunction(Parser.native_function("add(x, y)"), lambda x, y: x + y))
        term = Parser.term("a(1)")

        result = Interpreter(mod).interpret(term)

        self.assertEqual(result, IntTerm(2))

    def test_interpreter_caching(self):
        if_rule = Parser.rule("if(a) --> then(a)")
        then1_rule = Parser.rule("then(0) --> b")
        then2_rule = Parser.rule("then(x) --> c")
        module = Module([if_rule, then1_rule, then2_rule])
        interpreter = Interpreter(module)

        result1 = interpreter.interpret(Parser.term("if(0)"))
        self.assertEqual(VarTerm("b"), result1)

        result2 = interpreter.interpret(Parser.term("if(1)"))
        self.assertEqual(VarTerm("c"), result2)

    def test_recursive_contexts(self):
        ifz_rule = Parser.rule("ifz(cond, then, else) --> ifzc(value, then, else) where cond --> value")
        ifz0_rule = Parser.rule("ifzc(0, then, else) --> then")
        ifz1_rule = Parser.rule("ifzc(nonzero, then, else) --> else")  # TODO need inequality check, e.g. where non_zero != 0
        module = Module([ifz_rule, ifz0_rule, ifz1_rule])
        interpreter = Interpreter(module, 1)

        result = interpreter.interpret(Parser.term("ifz(ifz(1, 2, 3), 4, 5)"))
        self.assertEqual(IntTerm(5), result)


if __name__ == '__main__':
    unittest.main()
