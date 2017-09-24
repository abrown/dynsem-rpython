import unittest
from ..interpreter import *


# test cases
class TestEvaluation(unittest.TestCase):
    def test_transform(self):
        holes = ['a', 'b']
        sut = ConstructorNode(None, [1], {0: 'c'}, None)
        self.assertEqual(['c', 'b'], sut.transform(holes))


if __name__ == '__main__':
    unittest.main()
