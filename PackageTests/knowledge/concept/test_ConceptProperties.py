import unittest

class Test_ConceptPropertiesInterface(unittest.TestCase):

    def test_correctness(self):

        # No issue as the child does not take the parent attribute
        self.child.attr["a"] = 1
        self.parent.attr["a"] = 2

        del self.child.attr["a"]

        # The child should then differed back to he parents value for the attribute
        self.assertEqual(self.child.attr["a"], 2)

        self.fail()

    def test_inheritance(self):
        """ Cannot set concept property as None """
        self.fail()

    def test_Conflicting_inheritence(self):
        # Cannot inherit conflicting values for properties
        self.fail()

    def test_GettingAttributesShallGetConceptNotParent(self):
        # test that when collecting attributes, they are collected from the concept not its ancestors
        self.fail()

    def test_something(self):
        # length

                self.assertEqual(len(self.alone.attr), 0)

        self.alone.attr["a"] = 1
        self.alone.attr["b"] = 2

        self.assertEqual(len(self.alone.attr), 2)

        self.assertEqual(len(self.parent.attr), 0)
        self.assertEqual(len(self.child.attr), 0)

        self.parent.attr["a"] = 1
        self.parent.attr["b"] = 2

        self.assertEqual(len(self.parent.attr), 2)
        self.assertEqual(len(self.child.attr), 2)

