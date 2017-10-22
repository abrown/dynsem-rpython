import unittest

from src.meta.interpreter import Interpreter
from src.meta.parser import Parser
from src.meta.dynsem import Module
from src.meta.term import ApplTerm


class TestE2(unittest.TestCase):
    def test_rules(self):
        mod = Module()
        mod.rules.append(Parser.rule("block([x | xs]) --> block(xs) where x --> y"))
        mod.rules.append(Parser.rule("E |- assign(x, v) --> {x |--> v, E}"))
        mod.rules.append(Parser.rule("E |- retrieve(x) --> E[x]"))
        mod.rules.append(Parser.rule("if(cond, then, else) --> result where cond --> cond2; case cond2 of {0 => else --> result otherwise => then --> result}"))
        mod.rules.append(Parser.rule("while(cond, then) --> result where cond --> cond2; case cond2 of {0 => cond2 --> result otherwise => then --> result}"))

        term = Parser.term("block([1, 2, 3, 4])")

        #result = Interpreter().interpret(mod, term)

        #self.assertEqual(result, ApplTerm("block"))


if __name__ == '__main__':
    unittest.main()
