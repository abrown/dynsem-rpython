import unittest

from src.compile.handmade import Interpreter
from src.meta.dynsem import Module
from src.meta.parser import Parser
from src.meta.term import IntTerm, ApplTerm, VarTerm


class TestInterpreter(unittest.TestCase):
    def test_environment_assignment(self):
        term = Parser.term("assign(a, 1)")
        sut = Interpreter()
        a = sut.environment.locate_and_put("a", IntTerm(42))  # this should be overwritten

        result = sut.interpret(term)

        self.assertIsInstance(result, IntTerm)
        self.assertEqual(IntTerm(1), sut.environment.get(a))

    def test_environment_retrieval(self):
        term = Parser.term("retrieve(y)")
        sut = Interpreter()
        sut.environment.locate_and_put("y", IntTerm(42))

        result = sut.interpret(term)

        self.assertEqual(result, IntTerm(42))

    def test_reduction_premise(self):
        term = Parser.term("ifz(1, 42, 99)")

        result = Interpreter().interpret(term)

        self.assertEqual(IntTerm(42), result)

    def test_block(self):
        term = Parser.term("block([1, 2, 3, 4])")

        result = Interpreter().interpret(term)

        self.assertEqual(None, result)

    def test_native(self):
        term = Parser.term("add(1, 1)")

        result = Interpreter().interpret(term)

        self.assertEqual(result, IntTerm(2))

    def test_interpreter_caching(self):
        interpreter = Interpreter()

        result1 = interpreter.interpret(Parser.term("ifz(0, b, c)"))
        self.assertEqual(VarTerm("c"), result1)

        result2 = interpreter.interpret(Parser.term("ifz(1, b, c)"))
        self.assertEqual(VarTerm("b"), result2)

    def test_recursive_contexts(self):
        interpreter = Interpreter()

        result = interpreter.interpret(Parser.term("ifz(ifz(1, 2, 3), 4, 5)"))
        self.assertEqual(IntTerm(4), result)

    def test_sumprimes(self):
        program = """
        /* sum up all primes in [2..max], using inefficient algorithm from lecture 1. */
        block([
          assign(max, 50),
          assign(s, 0),
          assign(n, 2),
          while(leq(retrieve(n), retrieve(max)),
            block([
              assign(p, 1),  /* flag indicating primeness: initialize to true */
              assign(d, 2),
              while(leq(retrieve(d), sub(retrieve(n), 1)),
                block([           /* we have no mod operator... */
                  assign(m, mul(retrieve(d), div(retrieve(n), retrieve(d)))),
                  ifz(leq(retrieve(n), retrieve(m)),  /* always have m <= n */
                    assign(p, 0),  /* i.e., n = m, so d divides n, so set p false */
                    block()  /* (block) is a no-op */
                  ),
                  assign(d, add(retrieve(d), 1))
                ])
              ),
              ifz(retrieve(p),
                assign(s, add(retrieve(s), retrieve(n))),
                block()
              ),
              assign(n, add(retrieve(n), 1))
            ])
          ),
          write(retrieve(s))
        ])
        """

        interpreter = Interpreter()

        result = interpreter.interpret(Parser.term(program))

        self.assertEqual(None, result)
        self.assertEqual(328, interpreter.environment.locate_and_get('s').number)


if __name__ == '__main__':
    unittest.main()
