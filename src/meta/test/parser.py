import unittest

from ..parser import *


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

        self.assertEqual(ApplTerm("a", [VarTerm("x"), VarTerm("y")]), term)

    def test_parentheses(self):
        text = """
        rules
            Lit(s) --> NumV(parseI(s))
            Plus(NumV(a), NumV(b)) --> NumV(addI(a, b))
        """
        sut = Parser(text)

        module = sut.all()

        self.assertEqual(2, len(module.rules))
        self.assertEqual(ApplTerm("Lit", [VarTerm("s")]), module.rules[0].before)
        self.assertEqual(ApplTerm("NumV", [ApplTerm("addI", [VarTerm("a"), VarTerm("b")])]), module.rules[1].after)


if __name__ == '__main__':
    unittest.main()
