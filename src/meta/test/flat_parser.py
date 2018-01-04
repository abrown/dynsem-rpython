import unittest

from src.meta.flat_parser import FlatParser
from src.meta.term import Term, ApplTerm, VarTerm, IntTerm, ListTerm, ListPatternTerm, MapReadTerm, MapWriteTerm, \
    AssignmentTerm


class TestFlatParser(unittest.TestCase):
    def assertParsedTermEqual(self, text, expected):
        actual = FlatParser.term(text)
        self.assertEqual(expected.cells, actual.cells)
        self.assertEqual(expected.var_offsets, actual.var_offsets)

    def test_int(self):
        self.assertParsedTermEqual("42", Term([IntTerm(42)]))

    def test_var(self):
        self.assertParsedTermEqual("a", Term([VarTerm("a")], [0]))

    def test_empty_appl(self):
        self.assertParsedTermEqual("a()", Term([ApplTerm("a")]))

    def test_simple_appl(self):
        self.assertParsedTermEqual("a(b, 42)", Term([ApplTerm("a", 2, 2), VarTerm("b"), IntTerm(42)], [1]))

    def test_multi_var_appl(self):
        self.assertParsedTermEqual("a(b, c(d), e)", Term(
            [ApplTerm("a", 3, 4), VarTerm("b"), ApplTerm("c", 1, 3), VarTerm("d"), VarTerm("e")], [1, 2, 1]))

    def test_empty_list(self):
        self.assertParsedTermEqual("[]", Term([ListTerm()]))

    def test_list(self):
        self.assertParsedTermEqual("[1, 2, three]",
                                   Term([ListTerm(3, 3), IntTerm(1), IntTerm(2), VarTerm("three")], [3]))

    def test_list_pattern(self):
        self.assertParsedTermEqual("[x, y | zs]",
                                   Term([ListPatternTerm(3, 3), VarTerm("x"), VarTerm("y"), VarTerm("zs")], [1, 1, 1]))

    def test_map_read(self):
        self.assertParsedTermEqual("x[y]", Term([MapReadTerm(1), VarTerm("x"), VarTerm("y")], [1, 1]))

    def test_map_write(self):
        self.assertParsedTermEqual("{x |--> y, E}", Term(
            [MapWriteTerm(2, 4), AssignmentTerm(3), VarTerm("x"), VarTerm("y"), VarTerm("E")], [2, 1, 1]))

    # def test_header(self):
    #     text = """0
    #     """
    #
    #     sut = Parser(text)
    #
    #     self.assertEqual(sut.all().name, "trans/runtime/environment")
    #
    # def test_comments(self):
    #     text = """
    #     imports
    #         trans/runtime/a
    #         trans/runtime/b
    #     """
    #
    #     sut = Parser(text)
    #
    #     self.assertEqual(len(sut.all().imports), 2)
    #
    # def test_terms(self):
    #     text = """a(x, y)"""
    #
    #     term = Parser.term(text)
    #
    #     self.assertEqual(ApplTerm("a", [VarTerm("x"), VarTerm("y")]), term)
    #
    # def test_rules(self):
    #     text = """a(x, y) --> b where 1 == 1"""
    #
    #     parsed = Parser.rule(text)
    #
    #     expected = Rule(ApplTerm("a", [VarTerm("x", 0), VarTerm("y", 1)]), VarTerm("b"), None, None, 2)
    #     expected.premises.append(EqualityCheckPremise(IntTerm(1), IntTerm(1)))
    #
    #     self.assertEqual(expected, parsed)
    #
    # def test_parentheses(self):
    #     text = """
    #     rules
    #         Lit(s) --> NumV(parseI(s))
    #         Plus(NumV(a), NumV(b)) --> NumV(addI(a, b))
    #     """
    #     sut = Parser(text)
    #
    #     mod = sut.all()
    #
    #     self.assertEqual(2, len(mod.rules))
    #     self.assertEqual(ApplTerm("Lit", [VarTerm("s", 0)]), mod.rules[0].before)
    #     self.assertEqual(ApplTerm("NumV", [ApplTerm("addI", [VarTerm("a", 0), VarTerm("b", 1)])]), mod.rules[1].after)
    #
    # def test_environment_write(self):
    #     rule = Parser.rule("E |- bindVar(x, v) --> {x |--> v, E}")
    #
    #     self.assertIsInstance(rule.after, MapWriteTerm)
    #     self.assertEqual(2, len(rule.after.assignments))
    #     self.assertEqual(VarTerm("E"), rule.components[0])
    #
    # def test_environment_read(self):
    #     rule = Parser.rule("E |- read(x) --> E[x]")
    #
    #     self.assertIsInstance(rule.after, MapReadTerm)
    #     self.assertEqual(VarTerm("E"), rule.after.map)
    #     self.assertEqual(VarTerm("x", 0), rule.after.key)
    #
    # def test_case(self):
    #     premise = Parser.premise("case i of {1 => x --> y otherwise => y --> z}")
    #
    #     self.assertIsInstance(premise, CasePremise)
    #     self.assertEqual("i", premise.left.name)
    #     self.assertEqual(2, len(premise.values))
    #     self.assertEqual(2, len(premise.premises))
    #
    # def test_list(self):
    #     list = Parser.term("[a, b, 1, 2]")
    #
    #     self.assertIsInstance(list, ListTerm)
    #     self.assertEqual(4, len(list.items))
    #
    # def test_if(self):
    #     term = Parser.term("if(leq(1, 2), a(), b())")
    #
    #     self.assertIsInstance(term, ApplTerm)
    #     self.assertEqual(3, len(term.args))
    #     self.assertEqual("leq", term.args[0].name)
    #
    # def test_slot_assignment(self):
    #     rule = Parser.rule("block([x | xs]) --> block(xs) where x --> y")
    #
    #     self.assertEqual(3, rule.number_of_bound_terms)


if __name__ == '__main__':
    unittest.main()
