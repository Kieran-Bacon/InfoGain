import unittest, pytest

from infogain.knowledge import Ontology, Concept, Instance
from infogain.knowledge.concept import ConceptSet, FamilyConceptSet

class Test_Concept(unittest.TestCase):

    def test_initialisation_family_linking(self):

        person = Concept("Person", children={"Kieran", "Luke"})
        kieran = Concept("Kieran", parents={person})

        self.assertTrue(kieran in person.children)
        self.assertTrue(person in kieran.parents)
        self.assertTrue("Luke" in person.children)

    def test_ancestors_full_concepts(self):

        grandfather = Concept("Grand Father")
        father = Concept("Father", parents={grandfather})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {grandfather, father})

    def test_ancestors_partial_concepts(self):

        father = Concept("Father", parents={"Grand Father"})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {father, "Grand Father"})

        child = Concept("Child", parents={"John"})

        self.assertEqual(child.ancestors(), {"John"})

    def test_descendants_full_concepts(self):

        grandson = Concept("Grand Son")
        son = Concept("Son", children={grandson})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, grandson})

    def test_descendants_partial_concepts(self):

        son = Concept("Son", children={"Grand Son"})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, "Grand Son"})

        person = Concept("Person",children={"Son"})
        self.assertEqual(person.descendants(), {"Son"})

    def test_minimise(self):

        concept = Concept("Name")
        mini = concept.minimise()

        self.assertEqual(mini["name"], "Name")
        self.assertTrue(mini.get("parents", True))
        self.assertTrue(mini.get("permeable", True))
        self.assertTrue(mini.get("properties", True))
        self.assertTrue(mini.get("alias", True))

        concept = Concept("Name", parents={"Kieran"}, children={"What", "hey"})
        concept.alias.add("Badass")
        concept.properties["age"] = 24
        mini = concept.minimise()

        self.assertEqual(mini["name"], "Name")
        self.assertEqual(mini["parents"], ["Kieran"])
        self.assertFalse(mini.get("permeable", False))
        self.assertEqual(mini["properties"], {"age": 24})
        self.assertEqual(mini["alias"], ["Badass"])

    def test_expandConceptSet(self):
        """ Ensure that a concept is correct expanded into its children """

        ont = Ontology()

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})

        for concept in {x,x1,x11,x2,x12,y,y1,y11,y2}:
            ont.addConcept(concept)

        self.assertEqual(
            {con.name for con in Concept.expandConceptSet({x, y1})},
            {con.name for con in {x,x1,x2,x11,x12,y1,y11}}
        )
        self.assertEqual(Concept.expandConceptSet({x2, y}), {x2, y, y1, y2, y11})

    def test_minimiseConceptSet(self):
        """ """

        ont = Ontology()

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})

        for concept in {x,x1,x11,x2,x12,y,y1,y11,y2}:
            ont.addConcept(concept)

        self.assertEqual({c.name for c in Concept.minimiseConceptSet(Concept.expandConceptSet({x, y1}))}, {x, y1})

    def test_generation_of_concept_instance(self):
        """ Test that a concept generates its instance correctly and that it has the behaviour that
        we would want """

        # Test that an abstract concept raises an type error when attempting to generate its instance
        being = Concept("Being", properties={"age": int}, category="abstract")
        with pytest.raises(TypeError):
            being.instance()

        # Test that a static concept returns only a single instance regardless of the number of calls
        kieran = Concept("Kieran", properties={"age": 10}, category="static")

        firstKieranInst = kieran.instance()
        secondKieranInst = kieran.instance()

        self.assertTrue(firstKieranInst is secondKieranInst)
        self.assertTrue(kieran.properties is firstKieranInst.properties is secondKieranInst.properties)

        kieran.properties["lastname"] = "Bacon"

        self.assertEqual(firstKieranInst.lastname, "Bacon")
        self.assertEqual(secondKieranInst.lastname, "Bacon")

        # Test that a dynamic concept generates multiple differing instances with individual properties
        person = Concept("Person", properties={"age": 10})

        ben = person.instance("Ben")
        tom = person.instance("Tom")

        person.properties["lastname"] = "Bacon"

        self.assertEqual(ben.lastname, None)  # Does not have the new property

        tom.height = 6.4

        self.assertEqual(tom.height, 6.4)
        self.assertEqual(ben.height, None)

    def test_ConceptInstance_assignment(self):

        class PersonInstance(Instance):

            def something(self):
                return 10

        self.assertTrue(issubclass(PersonInstance, Instance))

        example = Concept("example", properties={"cool": 97})

        example.setInstanceClass(PersonInstance)

        inst = example.instance()

        self.assertEqual(inst.something(), 10)

    def test_concept_string_equality_in_dictionaries(self):

        example = Concept("example")

        collection = {example: 10}

        self.assertEqual(collection.get(example), 10)
        self.assertEqual(collection.get("example"), 10)

        collection2 = {"example": 10}

        self.assertEqual(collection2.get(example), 10)
        self.assertEqual(collection2.get("example"), 10)


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

        family = FamilyConceptSet()
        family.add(self.b)

        self.assertEqual(family, {self.b, self.c, self.d})

        family.add(self.f)

        self.assertEqual(family, {self.f, self.g})

    def test_linked(self):

        family = FamilyConceptSet()

        self.assertFalse(family.linked(self.a))
        self.assertFalse(family.linked("A"))

        family.add("A")

        self.assertFalse(family.linked(self.a))
        self.assertFalse(family.linked("A"))

    def test_partials(self):

        family  = FamilyConceptSet()

        family.add(self.g)
        family.add("G")
        self.assertEqual(family.partials(), {"G"})



if __name__ == "__main__":
    unittest.main()