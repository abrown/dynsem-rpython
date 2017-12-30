import unittest

from src.meta.parser import Parser
from src.meta.slot_assigner import SlotAssigner


class TestSlotAssigner(unittest.TestCase):
    def test_slots_on_terms(self):
        sut = SlotAssigner()
        term = Parser.term("a(b, c)")

        assigned = sut.assign_term(term)

        self.assertEqual(2, assigned)
        self.assertEqual(0, term.args[0].slot)
        self.assertEqual(1, term.args[1].slot)

    def test_slots_on_rules(self):
        sut = SlotAssigner()
        rule = Parser.rule("a(x) --> [z] where x == 1; b(y) => x; y --> z.")

        assigned = sut.assign_rule(rule.before, rule.after, rule.premises)

        self.assertEqual(3, assigned)
        self.assertEqual(0, rule.before.args[0].slot)  # a(x)
        self.assertEqual(0, rule.premises[0].left.slot)  # x == 1
        self.assertEqual(1, rule.premises[1].left.args[0].slot)  # b(y) => x
        self.assertEqual(0, rule.premises[1].right.slot)  # b(y) => x
        self.assertEqual(1, rule.premises[2].left.slot)  # y --> z
        self.assertEqual(2, rule.premises[2].right.slot)  # y --> z
        self.assertEqual(2, rule.after.items[0].slot)  # [z]

    def test_slots_on_block(self):
        sut = SlotAssigner()
        rule = Parser.rule("block([x | xs]) --> block(xs) where x --> y.")

        assigned = sut.assign_rule(rule.before, rule.after, rule.premises)

        self.assertEqual(3, assigned)


if __name__ == '__main__':
    unittest.main()
