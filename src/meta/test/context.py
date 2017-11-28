import unittest

from src.meta.context import Context, ContextError, SlotAssigner
from src.meta.parser import Parser
from src.meta.term import VarTerm, IntTerm, ListTerm


class TestContext(unittest.TestCase):
    def setUp(self):
        self.sut = Context(10)

    def bind(self, term1, term2):
        self.term1 = Parser.term(term1)
        SlotAssigner().assign_term(self.term1)  # need to do this here because slot assignments are made at the rule level
        self.term2 = Parser.term(term2)
        self.sut.bind(self.term1, self.term2)

    def assertResolves(self, name, value):
        if isinstance(value, int):
            value = IntTerm(value)
        elif isinstance(value, str):
            value = Parser.term(value)

        slotted_var = TestContext.__find_slot(self.term1, name)
        resolved = self.sut.resolve(slotted_var)

        self.assertEqual(resolved, value)

    @staticmethod
    def __find_slot(term, name):
        return term.walk(lambda t, a: t if isinstance(t, VarTerm) and t.name == name else None)

    def test_var(self):
        self.bind('a', 'b(1, 2)')
        self.assertResolves('a', 'b(1, 2)')

    def test_appl(self):
        self.bind('a(b, c)', 'a(1, 2)')
        self.assertResolves('b', 1)
        self.assertResolves('c', 2)

    def test_list(self):
        self.bind('[a, b, c]', '[1, 2, 3]')
        self.assertResolves('a', 1)
        self.assertResolves('b', 2)
        self.assertResolves('c', 3)

    def test_list_pattern(self):
        self.bind('[a|as]', '[1, 2, 3]')
        self.assertResolves('a', 1)
        self.assertResolves('as', ListTerm([IntTerm(2), IntTerm(3)]))

    def test_complex(self):
        self.bind('[a(b, [c|cs]), d]', '[a(1, [2, 3]), 4]')
        self.assertResolves('b', 1)
        self.assertResolves('c', 2)
        self.assertResolves('cs', ListTerm([IntTerm(3)]))
        self.assertResolves('d', 4)

    def test_error_number_of_terms(self):
        self.assertRaises(ContextError, self.bind, '[a]', '[1, 2]')

    def test_error_number_of_args(self):
        self.assertRaises(ContextError, self.bind, 'a(b, c)', 'a(1)')

    @unittest.skip("this check is done at a different level, e.g. in the rule-finding")
    def test_error_does_not_match(self):
        self.assertRaises(ContextError, self.bind, 'a(b, c)', 'b(1, 2)')

    def test_slots_on_terms(self):
        term = Parser.term("a(b, c)")

        assigned = SlotAssigner().assign_term(term)

        self.assertEqual(2, assigned)
        self.assertEqual(0, term.args[0].slot)
        self.assertEqual(1, term.args[1].slot)

    def test_slots_on_rules(self):
        rule = Parser.rule("a(x) --> [z] where x == 1; b(y) => x; y --> z.")

        assigned = SlotAssigner().assign_rule(rule)

        self.assertEqual(3, assigned)
        self.assertEqual(0, rule.before.args[0].slot)
        self.assertEqual(0, rule.premises[0].left.slot)
        self.assertEqual(1, rule.premises[1].left.args[0].slot)
        self.assertEqual(0, rule.premises[1].right.slot)
        self.assertEqual(1, rule.premises[2].left.slot)
        self.assertEqual(2, rule.premises[2].right.slot)
        self.assertEqual(2, rule.after.items[0].slot)


if __name__ == '__main__':
    unittest.main()
