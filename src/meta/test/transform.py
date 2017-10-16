import unittest

from ..parser import *
from ..transform import *


class TestTransform(unittest.TestCase):
    def test_header(self):
        sut = Module()
        sut.rules.append(Rule(Parser.term("a"), Parser.term("b"), [Parser.premise("a == 1")]))
        sut.rules.append(Rule(Parser.term("a"), Parser.term("b"), [Parser.premise("a == 2")]))

        sut = transform(sut)

        # TODO self.assertEqual(len(sut.rules), 1)


if __name__ == '__main__':
    unittest.main()
