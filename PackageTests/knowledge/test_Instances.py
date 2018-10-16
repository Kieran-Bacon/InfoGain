import unittest

from infogain.knowledge import Instance

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

class Test_ConceptInstance(unittest.TestCase):
    pass

class Test_RelationInstance(unittest.TestCase):
    pass