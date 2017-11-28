import unittest

from src.meta.dynsem import EqualityCheckPremise, Rule, CasePremise
from src.meta.parser import Parser
from src.meta.term import ApplTerm, VarTerm, IntTerm, MapReadTerm, MapWriteTerm, ListTerm


class TestParser(unittest.TestCase):
    def assertTermEqual(self, expected, actual):
        if len(expected) is not len(actual):
            raise AssertionError("Lengths do not match: {} != {}".format(expected, actual))
        for i, e in enumerate(expected):
            self.assertIsInstance(actual[i], e.__class__)
            self.assertEqual(e.location, actual[i].location) if e.location else None
            self.assertEqual(e.value, actual[i].value) if e.value else None

    def test_header(self):
        text = """
        module trans/runtime/environment
        """

        sut = Parser(text)

        self.assertEqual(sut.all().name, "trans/runtime/environment")

    def test_comments(self):
        text = """
        imports
            trans/runtime/a
            trans/runtime/b
        """

        sut = Parser(text)

        self.assertEqual(len(sut.all().imports), 2)

    def test_terms(self):
        text = """a(x, y)"""

        term = Parser.term(text)

        self.assertEqual(ApplTerm("a", [VarTerm("x", 0), VarTerm("y", 1)]), term)

    def test_rules(self):
        text = """a(x, y) --> b where 1 == 1"""

        parsed = Parser.rule(text)

        expected = Rule(ApplTerm("a", [VarTerm("x", 0), VarTerm("y", 1)]), VarTerm("b"))
        expected.premises.append(EqualityCheckPremise(IntTerm(1), IntTerm(1)))
        expected.slots = 2

        self.assertEqual(expected, parsed)

    def test_parentheses(self):
        text = """
        rules
            Lit(s) --> NumV(parseI(s))
            Plus(NumV(a), NumV(b)) --> NumV(addI(a, b))
        """
        sut = Parser(text)

        mod = sut.all()

        self.assertEqual(2, len(mod.rules))
        self.assertEqual(ApplTerm("Lit", [VarTerm("s")]), mod.rules[0].before)
        self.assertEqual(ApplTerm("NumV", [ApplTerm("addI", [VarTerm("a"), VarTerm("b")])]), mod.rules[1].after)

    def test_environment_write(self):
        rule = Parser.rule("E |- bindVar(x, v) --> {x |--> v, E}")

        self.assertIsInstance(rule.after, MapWriteTerm)
        self.assertEqual(2, len(rule.after.assignments))
        self.assertEqual(VarTerm("E"), rule.components[0])

    def test_environment_read(self):
        rule = Parser.rule("E |- read(x) --> E[x]")

        self.assertIsInstance(rule.after, MapReadTerm)
        self.assertEqual(VarTerm("E"), rule.after.map)
        self.assertEqual(VarTerm("x", 0), rule.after.key)

    def test_case(self):
        premise = Parser.premise("case i of {1 => x --> y otherwise => y --> z}")

        self.assertIsInstance(premise, CasePremise)
        self.assertEqual("i", premise.left.name)
        self.assertEqual(2, len(premise.values))
        self.assertEqual(2, len(premise.premises))

    def test_list(self):
        list = Parser.term("[a, b, 1, 2]")

        self.assertIsInstance(list, ListTerm)
        self.assertEqual(4, len(list.items))

    def test_if(self):
        term = Parser.term("if(leq(1, 2), a(), b())")

        self.assertIsInstance(term, ApplTerm)
        self.assertEqual(3, len(term.args))
        self.assertEqual("leq", term.args[0].name)


if __name__ == '__main__':
    unittest.main()
