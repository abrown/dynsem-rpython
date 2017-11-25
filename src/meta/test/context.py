import unittest

from src.meta.context import Context, ContextError
from src.meta.parser import Parser
from src.meta.term import VarTerm, IntTerm, Term, ListTerm


class TestContext(unittest.TestCase):
    def assertResolves(self, context, name, value):
        if not isinstance(value, Term):
            value = IntTerm(value)  # assume all non-terms are ints for this test suite
        self.assertEqual(context.resolve(VarTerm(name)), value)

    def test_var(self):
        sut = Context()

        sut.bind(Parser.term('a'), Parser.term('b(1, 2)'))

        self.assertResolves(sut, 'a', Parser.term('b(1, 2)'))

    def test_appl(self):
        sut = Context()

        sut.bind(Parser.term('a(b, c)'), Parser.term('a(1, 2)'))

        self.assertResolves(sut, 'b', 1)
        self.assertResolves(sut, 'c', 2)

    def test_list(self):
        sut = Context()

        sut.bind(Parser.term('[a, b, c]'), Parser.term('[1, 2, 3]'))

        self.assertResolves(sut, 'a', 1)
        self.assertResolves(sut, 'b', 2)
        self.assertResolves(sut, 'c', 3)

    def test_list_pattern(self):
        sut = Context()

        sut.bind(Parser.term('[a|as]'), Parser.term('[1, 2, 3]'))

        self.assertResolves(sut, 'a', 1)
        self.assertResolves(sut, 'as', ListTerm([IntTerm(2), IntTerm(3)]))

    def test_complex(self):
        sut = Context()

        sut.bind(Parser.term('[a(b, [c|cs]), d]'), Parser.term('[a(1, [2, 3]), 4]'))

        self.assertResolves(sut, 'b', 1)
        self.assertResolves(sut, 'c', 2)
        self.assertResolves(sut, 'cs', ListTerm([IntTerm(3)]))
        self.assertResolves(sut, 'd', 4)

    def test_error_number_of_terms(self):
        sut = Context()
        self.assertRaises(ContextError, sut.bind, Parser.term('[a]'), Parser.term('[1, 2]'))

    def test_error_number_of_args(self):
        sut = Context()
        self.assertRaises(ContextError, sut.bind, Parser.term('a(b, c)'), Parser.term('a(1)'))

    @unittest.skip("this check is done at a different leve, e.g. in the rule-finding")
    def test_error_does_not_match(self):
        sut = Context()
        self.assertRaises(ContextError, sut.bind, Parser.term('a(b, c)'), Parser.term('b(1, 2)'))


if __name__ == '__main__':
    unittest.main()
