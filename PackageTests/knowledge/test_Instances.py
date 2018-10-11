import unittest

from infogain.knowledge import Instance

class Test_Instance(unittest.TestCase):

    def test_function_behaviour(self):

        def concatinate(a, b):
            return a + b

        example = Instance()
        example.addFunction(concatinate)

        self.assertEqual(example.function("concatinate", "hello", "there"), "hellothere")
        self.assertEqual(example.function("concatinate", 1, 2), 3)

        def noparam():
            return "yep"

        secondexample = Instance()
        secondexample.addFunction(noparam)

        self.assertEqual(secondexample.function("noparam"), "yep")
        self.assertEqual(secondexample.property("noparam"), "yep")

        # test missing function
        self.assertIsNone(secondexample.function("something"))

    def test_property_behaviour(self):

        example = Instance()

        example.addProperty("prop", "value")

        self.assertEqual(example.property("prop"), "value")
        self.assertIsNone(example.property("something"))

class Test_ConceptInstance(unittest.TestCase):
    pass

class Test_RelationInstance(unittest.TestCase):
    pass