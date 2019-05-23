import unittest
import pytest

from infogain.knowledge.concept import Concept

class Test_ConceptAliasesInterface(unittest.TestCase):
    
    def setUp(self):

        self.alone = Concept("Alone")

        self.parent = Concept("Parent")
        self.child = (Concept("Child", parents={self.parent}))

    def test_len(self):

        self.assertEqual(len(self.alone.aliases), 0)

        self.alone.aliases.add("a")
        self.alone.aliases.add("b")

        self.assertEqual(len(self.alone.aliases), 2)

        # Hiearchy

        self.assertEqual(len(self.parent.aliases), 0)
        self.assertEqual(len(self.child.aliases), 0)

        self.parent.aliases.add("a")
        self.parent.aliases.add("b")

        self.assertEqual(len(self.parent.aliases), 2)
        self.assertEqual(len(self.child.aliases), 2)

        self.child.aliases.add("c")

        self.assertEqual(len(self.parent.aliases), 2)
        self.assertEqual(len(self.child.aliases), 3)

        self.parent.aliases.remove("a")

        self.assertEqual(len(self.parent.aliases), 1)
        self.assertEqual(len(self.child.aliases), 2)

    def test_iter(self):
        # Test that aliases can be iterated in a sense that makes sense

        self.alone.aliases.add("example")

        self.assertEqual(set(iter(self.alone.aliases)), {"example"})

        self.alone.aliases.add("something else")

        self.assertEqual(set(iter(self.alone.aliases)), {"example", "something else"})

        self.alone.aliases.discard("example")

        self.assertEqual(set(iter(self.alone.aliases)), {"something else"})


        # Parents  and child interaction

        self.parent.aliases.add("Parent")
        self.child.aliases.add("Child")

        self.assertEqual(set(iter(self.parent.aliases)), {"Parent"})
        self.assertEqual(set(iter(self.child.aliases)), {"Parent", "Child"})

        self.child.aliases.discard("Parent")

        self.assertEqual(set(iter(self.child.aliases)), {"Parent", "Child"})

    def test_contains(self):
        # Test that an alias becomes a member alias in the container

        self.alone.aliases.add("example")

        self.assertTrue("example" in self.alone.aliases)

        self.parent.aliases.add("Parent")
        self.child.aliases.add("Child")

        self.assertTrue("Parent" in self.child.aliases)
        self.assertTrue("Child" in self.child.aliases)

    def test_add(self):
        # Test adding of an alias

        self.assertEqual(len(self.alone.aliases), 0)

        self.alone.aliases.add("example")

        self.assertEqual(len(self.alone.aliases), 1)
        self.assertEqual(self.alone.aliases, {"example"})

        self.alone.aliases.add("another")

        self.assertEqual(len(self.alone.aliases), 2)
        self.assertEqual(self.alone.aliases, {"example", "another"})

        self.alone.aliases.add("example")

        self.assertEqual(len(self.alone.aliases), 2)
        self.assertEqual(self.alone.aliases, {"example", "another"})

        for unwantedType in [0, None, 0.0, 3e9, dict(), object, set]:
            with pytest.raises(TypeError):
                self.alone.aliases.add(unwantedType)


    def test_discarding(self):
        # Test that discarding of a concept works as expected

        self.alone.aliases.add("a")
        self.alone.aliases.add("b")

        self.assertEqual(len(self.alone.aliases), 2)

        self.assertTrue(self.alone.aliases.discard("a"))

        self.assertEqual(len(self.alone.aliases), 1)
        self.assertNotIn("a", self.alone.aliases)

        self.assertFalse(self.alone.aliases.discard("a"))

        for invalidType in [0, 0.0, float, dict(), None]:
           self.assertFalse(self.alone.aliases.discard(invalidType))

        #  Parents

        self.parent.aliases.add("Parent")
        self.child.aliases.add("Child")

        self.assertEqual(len(self.parent.aliases), 1)
        self.assertEqual(len(self.child.aliases), 2)

        self.assertFalse(self.child.aliases.discard("Parent"))

        self.assertTrue(self.parent.aliases.discard("Parent"))

        self.assertEqual(len(self.parent.aliases), 0)
        self.assertEqual(len(self.child.aliases), 1)

    def test_inherited(self):
        # Test that the correct inherited aliases are returned

        self.alone.aliases.add("a")
        self.alone.aliases.add("b")

        self.assertEqual(self.alone.aliases.inherited(), set())

        self.parent.aliases.add("a")
        self.parent.aliases.add("b")

        self.assertEqual(self.parent.aliases.inherited(), set())
        self.assertEqual(self.child.aliases.inherited(), {"a", "b"})



    def test_specific(self):
        # Test that the aliases specifically given to the concept are returned

        self.alone.aliases.add("a")
        self.alone.aliases.add("b")

        self.assertEqual(self.alone.aliases.specific(), {"a", "b"})

        self.parent.aliases.add("a")
        self.parent.aliases.add("b")

        self.assertEqual(self.parent.aliases.specific(), {"a", "b"})
        self.assertEqual(self.child.aliases.specific(), set())