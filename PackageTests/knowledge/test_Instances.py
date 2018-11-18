import unittest

from infogain.knowledge import Instance, Concept

class Test_Instance(unittest.TestCase):

    def test_function_behaviour(self):

        def concatinate(a, b):
            return a + b

        example = Instance("x")
        example.concatinate = concatinate

        self.assertEqual(example.concatinate("hello", "there"), "hellothere")
        self.assertEqual(example.concatinate(1, 2), 3)

    def test_property_behaviour(self):

        example = Instance("x", properties={"prop": "value"})

        self.assertEqual(example.prop, "value")
        self.assertIsNone(example.something)

    def test_equality_string(self):

        self.assertTrue("England" == Instance("England"))
        self.assertFalse("England" == Instance("England", "uuid"))
        self.assertTrue("England" == Instance("Country", "England"))

    def test_equality_concept(self):
        
        england = Concept("England")
        
        self.assertTrue(england == Instance("England"))
        self.assertFalse(england == Instance("England", "uuid"))
        self.assertTrue(england == Instance("Country", "England"))

    def test_equality_instance(self):

        england = Instance("England")

        self.assertTrue(england == Instance("England"))
        self.assertFalse(england == Instance("England", "uuid"))
        self.assertTrue(england == Instance("Country", "England"))