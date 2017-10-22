import unittest

from src.meta.parser import Parser


class TestTerm(unittest.TestCase):
    def test_term_equality(self):
        a1 = Parser.term("a(x, y)")
        a2 = Parser.term("a(x, y)")

        self.assertTrue(a1 == a2)
        self.assertEqual(a1, a2)

    def test_term_matching(self):
        a1 = Parser.term("a(x, y)")
        b = Parser.term("b")

        self.assertTrue(b.matches(a1))
        self.assertFalse(a1.matches(b))

    def test_constructor_matching(self):
        a1 = Parser.term("a(1)")
        ax = Parser.term("a(x)")

        self.assertTrue(ax.matches(a1))

    def test_list_constructor(self):
        list = Parser.term("[a, b, 1, 2]")
        pattern = Parser.term("[x | xs]")

        self.assertTrue(pattern.matches(list))

if __name__ == '__main__':
    unittest.main()
