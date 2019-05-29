import unittest

from infogain.knowledge import Concept, Instance
from infogain.knowledge.concept import ConceptSet, FamilyConceptSet

class Test_ConceptSet(unittest.TestCase):
    """ These tests test the ConceptSet itself specifically """

    def setUp(self):

        self.c1 = Concept("1")
        self.c2 = Concept("2")
        self.c3 = Concept("3")

        self.non_family = [self.c1, self.c2, self.c3]

        self.f1 = Concept("a", children={"b"})
        self.f2 = Concept("b", parents={self.f1})
        self.f3 = Concept("c", parents={self.f2})

        self.family = [self.f1, self.f2, self.f3]

    def test_initialise(self):

        # Created a set of concepts that do not have any family connect at all
        cs = ConceptSet(self.non_family)
        self.assertTrue(len(cs) == 3)
        for e in cs: self.assertIn(e, self.non_family)

        # Created another connection where they are all family connected
        fs = ConceptSet(self.family)
        self.assertTrue(len(cs) == 3)
        for e in fs: self.assertIn(e, self.family)

    def test_add(self):
        """ Testing that the add function works as we intend it to """

        group = ConceptSet()

        # Show that it can allow str to be added
        # Show that it can allow concepts to be added
        # Show that it can allow Instances to be added
        to_be_added = ["example", Concept("Example 2"), Instance("Example 3", "The intruder")]

        for item in to_be_added:
            group.add(item)

        self.assertEqual(len(group), 3)
        for item in group:
            self.assertIn(item, to_be_added)

    def test_add_partials(self):
        """ Show that an item (that is a string) is added only partially, such that when you add the full concept, it is
        replaced """

        group = ConceptSet()
        group.add(self.c1)
        group.add("2")

        self.assertEqual(len(group), 2)

        group.add(self.c2)

        self.assertEqual(len(group), 2)
        for item in group:
            self.assertTrue(isinstance(item, Concept))

    def test_discard(self):
        # Test the discard function works as expected


        group = ConceptSet([self.c1, "2", self.f1, "example"])

        self.assertIn(self.c1, group)
        self.assertEqual(group.partials(), {"2", "example"})

        self.assertFalse(group.discard("3"))
        self.assertFalse(group.discard(self.c3))

        # True as concept 2 shall be equivalent to the partial "2"
        self.assertTrue(group.discard(self.c2))
        self.assertEqual(group.partials(), {"example"})

        # True as string is equivalent to concept
        self.assertTrue(group.discard("1"))
        self.assertEqual(group, {self.f1, "example"})


        self.assertTrue(group.discard(self.f1))
        self.assertTrue(group.discard("example"))

        self.assertEqual(group, set())


    def test_remove(self):
        """ Test that removing an item correctly removes the item - plus that string or concepts being passed also
        triggers a removal of the concepts
        """
        group = ConceptSet()

        # Tested adding and removing a single item
        group.add(self.c1)

        self.assertTrue(group)
        self.assertEqual(len(group), 1)

        group.remove(self.c1)

        self.assertFalse(group)
        self.assertEqual(len(group), 0)

        # Test the adding and removal of concepts and strings
        group.add(Concept("Test"))
        self.assertTrue(group)
        group.remove("Test")
        self.assertFalse(group)

        group.add("Test")
        self.assertTrue(group)
        group.remove(Concept("Test"))
        self.assertFalse(group)

    def test_expand(self):
        """ Show that expanding a conceptSet can only be done on the family path - and show that it can do eithe way """

        # Expansion doesn't occur with concepts that do not have family links
        s1 = ConceptSet([self.c1])
        s1.expand(True)

        self.assertEqual({self.c1}, s1)

        s1.expand(False)

        self.assertEqual({self.c1}, s1)

        # Test for expansion with family set
        s2 = ConceptSet([self.f2])

        s2.expand(True)

        self.assertEqual({self.f2, self.f3}, s2)

        s2.expand(False)

        self.assertEqual({*self.family}, s2)

    def test_expanded(self):
        """ Assert that a concept set can provide a new set with the correct contents without affecting the old set """

        s1 = ConceptSet([self.f2])

        s2 = s1.expanded(True)

        self.assertNotEqual(s1, s2)
        self.assertEqual({self.f2, self.f3}, s2)

        s3 = s1.expanded(False)

        self.assertNotEqual(s1, s3)
        self.assertNotEqual(s2, s3)

        self.assertEqual({self.f1, self.f2}, s3)

    def test_minimise(self):
        """ Assert that a concept set shall minimise along a given family line """

        s1 = ConceptSet([self.f2, self.f3])

        s1.minimise()

        self.assertEqual({self.f2}, s1)

        s2 = ConceptSet([self.f1, self.f2, self.f3])

        s2.minimise(False)

        self.assertEqual(s2, {self.f3})

    def test_minimised(self):

        s1 = ConceptSet([*self.family, *self.non_family])

        s2 = s1.minimised()

        self.assertNotEqual(s1, s2)
        self.assertEqual({self.f1, *self.non_family}, s2)

    def test_toStringSet(self):

        self.assertEqual(ConceptSet([*self.family, *self.non_family]), {"1","2","3","a","b","c"})

    def test_union(self):
        """ Test that the ConceptSet union shall return a new Concept with all unique concepts that appear in both """

        #

        a = ConceptSet(self.non_family)
        b = ConceptSet(self.family)

        c = a.union(b)

        self.assertEqual(c,  {*self.non_family, *self.family})

        # Test that partial concepts are still partial and that overwrites occur correctly

        a = ConceptSet([self.c1, "2", "3"])
        b = ConceptSet([self.c1, self.c2])

        c = a.union(b)

        self.assertEqual(a, {self.c1, self.c2, "3"})

    def test_intersection(self):

        # Find the intersection of the sets
        a = ConceptSet(self.non_family)
        b = ConceptSet([self.c1, self.c2])
        c = a.intersection(b)

        self.assertEqual(c, {self.c1, self.c2})

        # Works with partial items
        a = ConceptSet([self.c1, "2", "3", "4"])
        b = ConceptSet([self.c1, self.c2, "3"])
        self.assertEqual(a.intersection(b), b.intersection(a))
        c = a.intersection(b)

        self.assertEqual(c, {self.c1, self.c2, "3"})

    def test_difference(self):
        a = ConceptSet([*self.non_family, self.f2])
        b = ConceptSet([*self.non_family, self.f1])

        self.assertEqual(a.difference(b), {self.f2})
        self.assertEqual(b.difference(a), {self.f1})

        a = ConceptSet([self.c1, "2"])
        b = ConceptSet([self.c1, self.c3])

        self.assertEqual(a.difference(b), {"2"})
        self.assertEqual(b.difference(a), {self.c3})

    def test_partials(self):

        a = ConceptSet(self.family)
        a.add("1")
        a.add("2")

        self.assertEqual(a.partials(), {"1", "2"})

        a.add(self.c1)

        self.assertEqual(a.partials(), {"2"})


    def test_copy(self):

        a = ConceptSet(self.family)
        a.add(self.c1)

        self.assertEqual(a, {*self.family, self.c1})

class Test_FamilyConceptSet(unittest.TestCase):
    """ """

    def setUp(self):
        """
         A      E
         B      F
        C D     G
        """

        self.a, self.e = Concept("A"), Concept("E")
        self.b, self.f = Concept("B", parents={self.a}), Concept("F", parents={self.e})
        self.c, self.d= Concept("C", parents={self.b}), Concept("D", parents={self.b})
        self.g = Concept("G", parents={self.f})

    def test_add(self):
        # Test the adding of concepts to a family set provided the expected value

        self.assertEqual(self.b.parents, {self.a})
        self.assertEqual(self.b.children, {self.c, self.d})
        self.assertEqual(self.b.descendants(), {self.c, self.d})

        self.b.children.add(self.f)

        self.assertEqual(self.b.children, {self.c, self.d, self.f})
        self.assertEqual(self.b.descendants(), {self.c, self.d, self.f, self.g})

    def test_multipleAdds(self):
        # Ensure that multiple adds don't lead to unwanted behaviour with other items
        # If you inherited from a concept twice because you added it twice, when you remove the concept, it shall not
        # correct itself.
        self.fail()

    def test_discard(self):
        self.fail()