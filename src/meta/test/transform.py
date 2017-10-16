import unittest
from ..transform import *
from ..dynsem import *
from ..term import *


class TestTransform(unittest.TestCase):

    def test_header(self):
        sut = Module()
        sut.rules.append(Rule(Term.of("a"), Term.of("b"), [Premise.of("a == 1")]))
        sut.rules.append(Rule(Term.of("a"), Term.of("b"), [Premise.of("a == 2")]))

        sut = transform(sut)

        self.assertEqual(len(sut.rules), 1)


if __name__ == '__main__':
    unittest.main()
