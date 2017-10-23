import unittest

from src.meta.interpreter import Interpreter
from src.meta.parser import Parser
from src.meta.dynsem import Module, NativeFunction
from src.meta.term import ApplTerm


class TestE2(unittest.TestCase):
    def test_rules(self):
        mod = Module()
        mod.rules.append(Parser.rule("block([x | xs]) --> block(xs) where x --> y"))
        mod.rules.append(Parser.rule("E |- assign(x, v) --> {x |--> v, E}"))
        mod.rules.append(Parser.rule("E |- retrieve(x) --> E[x]"))
        mod.rules.append(Parser.rule("if(cond, then, else) --> result where case cond of {0 => result => else otherwise => result => then}"))
        mod.rules.append(Parser.rule("while(cond, then) --> result where case cond of {0 => result => cond otherwise => then --> result}"))

        mod.native_functions.append(NativeFunction(Parser.term("write(x)"), lambda x: print(x)))
        mod.native_functions.append(NativeFunction(Parser.term("add(x, y)"), lambda x, y: x + y))
        mod.native_functions.append(NativeFunction(Parser.term("sub(x, y)"), lambda x, y: x - y))
        mod.native_functions.append(NativeFunction(Parser.term("mul(x, y)"), lambda x, y: x * y))
        mod.native_functions.append(NativeFunction(Parser.term("div(x, y)"), lambda x, y: x / y))
        mod.native_functions.append(NativeFunction(Parser.term("leq(x, y)"), lambda x, y: int(x <= y)))

        #term = Parser.term("block([if(, 2, 3, 4])")
        term = Parser.term("if(leq(2, 1), a(), b())")

        result = Interpreter().interpret(mod, term)

        self.assertEqual(result, ApplTerm("b"))


if __name__ == '__main__':
    unittest.main()
