import unittest

from ..parser import *


# test cases
class TestEvaluation(unittest.TestCase):

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

        self.assertEqual(sut.parse_all().name, "trans/runtime/environment")

    def test_comments(self):
        text = """
        imports
            trans/runtime/a
            trans/runtime/b
        """

        sut = Parser(text)

        self.assertEqual(len(sut.parse_all().imports), 2)

    def test_terms(self):
        text = """a(x, y)"""
        sut = Parser(text)

        term = sut.parse_term()

        self.assertEqual(ApplTerm("a", [ApplTerm("x"), ApplTerm("y")]), term)

    def test_parentheses(self):
        text = """
        rules
            Lit(s) --> NumV(parseI(s))
            Plus(NumV(a), NumV(b)) --> NumV(addI(a, b))
        """
        sut = Parser(text)

        module = sut.parse_all()

        self.assertEqual(2, len(module.rules))
        self.assertEqual(ApplTerm("Lit", [ApplTerm("s")]), module.rules[0].before)
        self.assertEqual(ApplTerm("NumV", [ApplTerm("addI", [ApplTerm("a"), ApplTerm("b")])]), module.rules[1].after)


    # def test_rules(self):
    #     text = "E |- bindVar(x, v) --> {x |--> v, E}"
    #     sut = Tokenizer(text)
    #
    #     tokens = [sut.next() for i in range(17)]
    #
    #     self.assertIsInstance(tokens[15], RightBraceToken)
    #     self.assertIsInstance(tokens[16], EofToken)

if __name__ == '__main__':
    unittest.main()
