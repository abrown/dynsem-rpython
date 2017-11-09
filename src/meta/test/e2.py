import unittest

from src.meta.e2 import e2
from src.meta.interpreter import Interpreter
from src.meta.parser import Parser
from src.meta.term import ApplTerm, IntTerm


class TestE2(unittest.TestCase):
    def test_if(self):
        term = Parser.term("ifz(leq(2, 1), a(), b())")

        result = Interpreter(e2).interpret(term)

        self.assertEqual(result, ApplTerm("b"))

    def test_block_environment(self):
        term = Parser.term("block([assign(a, 1), write(retrieve(a))])")

        result = Interpreter(e2).interpret(term)

        self.assertEqual(result, ApplTerm("block"))
        self.assertEqual(len(result.args), 0)

    def test_while(self):
        interpreter = Interpreter(e2)
        program = """
        block([
          assign(a, 0),
          while(leq(retrieve(a), 10), 
            block([assign(a, add(retrieve(a), 1)), write(retrieve(a))])
          )
        ])
        """
        term = Parser.term(program)
        result = interpreter.interpret(term)

        self.assertEqual(interpreter.environment['a'], IntTerm(11))
        self.assertEqual(result, ApplTerm("block"))
        self.assertEqual(len(result.args), 0)

    def test_multi_resolution(self):
        program = """
        block([
          assign(a, 1),
          assign(a, add(retrieve(a), 1))
        ])
        """
        term = Parser.term(program)
        interpreter = Interpreter(e2)

        interpreter.interpret(term)

        self.assertEqual(interpreter.environment['a'], IntTerm(2))

    def test_sumprimes(self):
        program = """
        /* sum up all primes in [2..max], using 
            inefficient algorithm from lecture 1. */
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

        term = Parser.term(program)
        interpreter = Interpreter(e2)

        # TODO fix that E somehow gets saved on the environment
        interpreter.interpret(term)

        # 328 seems about right: http://www.wolframalpha.com/input/?i=sum+primes+up+to+50&x=0&y=0
        self.assertEqual(interpreter.environment["s"], IntTerm(328))


if __name__ == '__main__':
    unittest.main()
