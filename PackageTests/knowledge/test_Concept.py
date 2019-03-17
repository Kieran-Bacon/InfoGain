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

    def test_ancestores_partial_concepts(self):

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
        self.fail()

    def test_expanded(self):
        self.fail()

    def test_minimise(self):
        self.fail()

    def test_minimised(self):
        self.fail()

    def test_toStringSet(self):
        self.fail()

    def test_union(self):
        self.fail()

    def test_intersection(self):
        self.fail()

    def test_difference(self):
        self.fail()

    def test_copy(self):
        self.fail()

class Test_FamilyConceptSet(unittest.TestCase):
    """ """

    def test_add(self):
        self.fail()

if __name__ == "__main__":
    unittest.main()