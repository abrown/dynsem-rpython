import unittest
from ..transform import *
from ..dynsem import *
from ..parser import *


class TestTransform(unittest.TestCase):

    def test_header(self):
        sut = Module()
        sut.rules.append(Rule(Parser.parse_term("a"), Parser.parse_term("b"), [Parser.parse_premise("a == 1")]))
        sut.rules.append(Rule(Parser.parse_term("a"), Parser.parse_term("b"), [Parser.parse_premise("a == 2")]))

        sut = transform(sut)

        # TODO self.assertEqual(len(sut.rules), 1)


if __name__ == '__main__':
    unittest.main()
