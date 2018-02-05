import unittest
import ast
import astor

from src.meta.e2 import e2
from src.compile.compiler import Compiler
from src.meta.parser import Parser


if_tree = """
if term_hash == 1:
    print(term)
elif term_hash == 2:
    print(term)
elif term_hash == 3:
    print(term)
"""

class TestCompiler(unittest.TestCase):
    def test_constructing_if_tree(self):
        expected_tree = ast.parse(if_tree).body[0]
        id_mapping = {1: [{}], 2: [{}], 3: [{}]}

        actual_tree = Compiler.construct_if_tree(id_mapping)

        expected = astor.to_source(expected_tree)
        actual = astor.to_source(actual_tree)
        self.assertEqual(expected, actual)

    def test_compilation(self):
        compiler = Compiler()
        source = compiler.compile(e2)
        print(source) # for visual verification
        self.assertIn('elif term_hash == 4:', source)

    def test_constructing_body(self):
        compiler = Compiler()
        ast = compiler.construct_body(Parser.rule("a(b) --> c where b == 1; b --> d(c)"))

        self.assertEqual("asdf" , astor.to_source(ast))

if __name__ == '__main__':
    unittest.main()
