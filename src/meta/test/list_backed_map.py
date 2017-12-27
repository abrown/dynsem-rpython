import unittest

from src.meta.list_backed_map import ListBackedMap


class TestMap(unittest.TestCase):
    def test_simple_put_and_get(self):
        sut = ListBackedMap()

        i = sut.locate("a")
        sut.put(i, 42)

        self.assertEqual(42, sut.get(i))

    def test_simple_get_no_put(self):
        sut = ListBackedMap()

        i = sut.locate("b")

        self.assertEqual(None, sut.get(i))

    def test_put_multiple(self):
        sut = ListBackedMap()

        a = sut.locate("a")
        b = sut.locate("b")
        c = sut.locate("c")

        sut.put(c, "...")
        sut.put(a, 42)

        self.assertEqual(42, sut.get(a))
        self.assertEqual(None, sut.get(b))
        self.assertEqual("...", sut.get(c))

    def test_empty_without_locate(self):
        sut = ListBackedMap()

        with self.assertRaises(IndexError):
            sut.get(42)

        with self.assertRaises(IndexError):
            sut.put(42, "abc")

    def test_empty_locate(self):
        sut = ListBackedMap()

        i = sut.locate("x")

        self.assertEqual(0, i)

    def test_locate_and_etc(self):
        sut = ListBackedMap()

        self.assertEqual(0, sut.locate_and_put("a", 42))
        self.assertEqual(1, sut.locate_and_put("b", 43))

        self.assertEqual(43, sut.locate_and_get("b"))
        self.assertEqual(42, sut.locate_and_get("a"))


if __name__ == '__main__':
    unittest.main()
