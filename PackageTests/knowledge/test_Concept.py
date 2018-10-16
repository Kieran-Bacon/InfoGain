import unittest, pytest

from infogain.knowledge import Ontology, Concept, Instance

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

        self.assertEqual({con.name for con in Concept.expandConceptSet({x, y1})},{con.name for con in {x,x1,x2,x11,x12,y1,y11}})
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


if __name__ == "__main__":
    unittest.main()