import unittest

from infogain.information import Vertice
from infogain.knowledge import Concept, Instance

class Test_Vertices(unittest.TestCase):

    def test_vertice_equality(self):
        """ The aim is to ensure that classes that inherit from vertice
        are able to be compaired """

        a = Concept("a")
        a2 = Concept("a")
        b = Concept("b")

        self.assertEqual(a, a2)
        self.assertNotEqual(a, b)

        ai = Instance("a")

        self.assertEqual(a, ai)
        self.assertNotEqual(b, ai)

    def test_string_equality(self):

        a = Concept("a")

        self.assertEqual(a, "a")