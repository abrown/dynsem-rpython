import unittest

from src.compile.context import Context, ContextError
from src.meta.parser import Parser


class TestContext(unittest.TestCase):
    def bind(self, term):
        self.context = Context()
        self.context.bind(Parser.term(term))

    def assertResolves(self, name, expected_path):
        self.assertIn(name, self.context.bound_names)
        actual_path = ".".join(self.context.bound_names[name])
        self.assertEqual(expected_path, actual_path)

    def test_var(self):
        self.bind('x(a, b)')
        self.assertResolves('a', 'term.args[0]')
        self.assertResolves('b', 'term.args[1]')

    def test_list(self):
        self.bind('x([a, b, c])')
        self.assertResolves('a', 'term.args[0].items[0]')
        self.assertResolves('b', 'term.args[0].items[1]')
        self.assertResolves('c', 'term.args[0].items[2]')

    def test_list_pattern(self):
        self.bind('x([a|as])')
        self.assertResolves('a', 'term.args[0].items[0]')
        self.assertResolves('as', 'term.args[0].items[1:]')

    def test_complex(self):
        self.bind('x([a(b, [c|cs]), d])')
        self.assertResolves('b', 'term.args[0].items[0].args[0]')
        self.assertResolves('c', 'term.args[0].items[0].args[1].items[0]')
        self.assertResolves('cs', 'term.args[0].items[0].args[1].items[1:]')
        self.assertResolves('d', 'term.args[0].items[1]')


if __name__ == '__main__':
    unittest.main()
