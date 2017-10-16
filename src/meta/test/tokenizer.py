import unittest

from ..tokenizer import *


class TestTokenizer(unittest.TestCase):
    def assertTokensEqual(self, expected, actual):
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

        sut = Tokenizer(text)

        self.assertIsInstance(sut.next(), KeywordToken)

    def test_comments(self):
        text = """
        // avoid this
        /*
        and this
        // and even this
        /* most certainly this 
        */
        imports
            trans/runtime/values

        signature
            sort aliases
        """
        sut = Tokenizer(text)

        token = sut.next()

        self.assertEqual(token.value, "imports")

    def test_operators(self):
        text = """
        signature
            sort aliases
                Env = Map(String, V)
        """
        sut = Tokenizer(text)

        tokens = [sut.next() for i in range(5)]

        self.assertIsInstance(tokens[4], OperatorToken)
        self.assertEqual(tokens[4].value, '=')

    def test_parentheses(self):
        text = """
        arrows
            bindVar(String, V) --> Env
        """
        sut = Tokenizer(text)

        tokens = [sut.next() for i in range(7)]

        expected = [LeftParensToken(), IdToken(None, 'String'), CommaToken(), IdToken(None, 'V'), RightParensToken()]
        self.assertTokensEqual(expected, tokens[2:7])

    def test_rules(self):
        text = "E |- bindVar(x, v) --> {x |--> v, E}"
        sut = Tokenizer(text)

        tokens = [sut.next() for i in range(17)]

        self.assertIsInstance(tokens[15], RightBraceToken)
        self.assertIsInstance(tokens[16], EofToken)

    def test_paths_with_numbers(self):
        # must start with a letter
        text = "a/b/c/1"
        sut = Tokenizer(text)

        token = sut.next()
        eof = sut.next()

        self.assertIsInstance(token, IdToken)
        self.assertEqual(token.value, "a/b/c/1")
        self.assertIsInstance(eof, EofToken)


if __name__ == '__main__':
    unittest.main()
