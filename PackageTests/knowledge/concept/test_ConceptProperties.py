import unittest
import pytest

from infogain.knowledge import Concept

class Test_ConceptPropertiesInterface(unittest.TestCase):

    def setUp(self):

        self.alone = Concept("Alone")

        self.parent = Concept("Parent")
        self.child = Concept("Child", parents={self.parent})

    def test_len(self):
        self.assertEqual(len(self.alone.properties), 0)

        self.alone.properties["a"] = 1
        self.alone.properties["b"] = 2

        self.assertEqual(len(self.alone.properties), 2)

        self.assertEqual(len(self.parent.properties), 0)
        self.assertEqual(len(self.child.properties), 0)

        self.parent.properties["a"] = 1
        self.parent.properties["b"] = 2

        self.assertEqual(len(self.parent.properties), 2)
        self.assertEqual(len(self.child.properties), 2)

    def test_iter(self):
        
        self.alone.properties.update({"a": 1, "b": 2})

        for key in self.alone.properties:
            self.assertTrue(key == "a" or key == "b")

        self.assertEqual(set(self.alone.properties.keys()), {"a", "b"})
        self.assertEqual(set(self.alone.properties.values()), {1, 2})

        self.assertEqual(set((k, v) for k, v in self.alone.properties.items()), {("a", 1), ("b", 2)})

        # 
        self.parent.properties["a"] = 1
        self.child.properties["b"] = 2

        self.assertEqual(set(self.parent.properties.keys()), {"a"})
        self.assertEqual(set(self.child.properties.keys()), {"a", "b"})

        self.assertEqual(set(self.parent.properties.values()), {1})
        self.assertEqual(set(self.child.properties.values()), {1, 2})

        self.assertEqual(set((k, v) for k, v in self.parent.properties.items()), {("a", 1)})
        self.assertEqual(set((k, v) for k, v in self.child.properties.items()), {("a", 1), ("b", 2)})

    def test_setgetdel(self):

        # Test that None cannot be given as a value for a property        
        with pytest.raises(ValueError):
            self.alone.properties["a"] = None

        self.alone.properties["a"] = 1

        self.assertEqual(self.alone.properties["a"], 1)

        del self.alone.properties["a"]

        with pytest.raises(KeyError):
            self.alone.properties["a"]

        self.parent.properties["a"] = 1
        self.child.properties["b"] = 2

        self.assertEqual(self.parent.properties["a"], 1)
        self.assertEqual(self.child.properties["a"], 1)
        self.assertEqual(self.child.properties["b"], 2)

        # Attempt to delete inherited value and fail
        with pytest.raises(KeyError):
            del self.child.properties["a"]

        self.assertEqual(self.child.properties["a"], 1)

class test_ConceptProperties(unittest.TestCase):

    def setUp(self):

        self.alone = Concept("Alone")

        self.parent1 = Concept("Parent1")
        self.parent2 = Concept("Parent2")
        self.child = Concept("Child", parents={self.parent1, self.parent2})

    def test_updatingConceptPropertyAllowsInheritedToCascade(self):

        # No issue as the child does not take the parent attribute
        self.child.properties["a"] = 1
        self.parent1.properties["a"] = 2

        del self.child.properties["a"]

        # The child should then differed back to he parents value for the attribute
        self.assertEqual(self.child.properties["a"], 2)

    def test_MultipartProperties(self):

        self.parent1.properties["a"] = 1
        self.parent2.properties["a"] = 2

        self.assertEqual(self.child.properties["a"], {1, 2})

    def test_gettingAttributesShallGetConceptNotParent(self):
        # test that when collecting attributes, they are collected from the concept not its ancestors

        self.parent1.properties["a"] = 1
        self.child.properties["a"] = 2

        self.assertEqual(self.child.properties["a"], 2)

        self.child.properties["b"] = 3
        self.parent1.properties["b"] = 4

        self.assertEqual(self.child.properties["b"], 3)