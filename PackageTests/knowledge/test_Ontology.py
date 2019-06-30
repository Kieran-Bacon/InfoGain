import unittest, pytest, os, json

from infogain.knowledge import Ontology, Concept, Relation
from infogain import Serialiser
from infogain.resources.ontologies import language as Language


class Test_Ontology_Creation(unittest.TestCase):

    def setUp(self):
        self.person = Concept("Person", children={"Kieran"})
        self.kieran = Concept("Kieran", parents={self.person})

        self.language = Concept("Language", children={"English"})
        self.english = Concept("English", parents={self.language})

        self.speaks = Relation({self.person}, "speaks", {self.language})

        self.maxDiff = None

    def test_builtins(self):

        emptyOnt = Ontology()

        self.assertEqual(emptyOnt._concepts, {})

        emptyOnt.importBuiltin("time")

        self.assertIsNotNone(emptyOnt.concepts("Time"))

        with pytest.raises(ImportError):
            emptyOnt.importBuiltin("NotAModule")

    @unittest.skip("Saving is going to change soon")
    def test_load_and_save(self):
        """ Test that saving and ontology returns it to the same state as it was before """

        ont = Language.ontology()

        with open(Language.path_ontology, "r") as handler:
            content = handler.read()

        self.assertEqual(content, Serialiser("json").dump(ont))

    def test_Concepts_Ontology(self):

        ontology = Ontology("Sample")

        ontology.concepts.add(self.kieran)
        ontology.concepts.add(self.person)

        self.assertEqual(ontology.concepts("Person"), self.person)
        self.assertEqual(ontology.concepts("Kieran"), self.kieran)
        self.assertEqual(ontology.concepts("Dave"), None)

    def test_Relations_Ontology(self):

        ontology = Ontology("Sample")

        for concept in [self.kieran, self.person, self.english, self.language]:
            ontology.concepts.add(concept)

        ontology.relations.add(self.speaks)

        self.assertEqual(ontology.relations("speaks"), self.speaks)
        self.assertEqual(ontology.relations("placeholder"), None)

    def test_Relations_Clone_Ontology(self):

        ontology = Ontology("Test1")

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})

        for con in [x,x1,x11,x12,x2,y,y1,y2,y11]:
            ontology.concepts.add(con)

        rel = Relation([[x1], [x2]], "rel", [[y1], [y2]])

        ontology.relations.add(rel)

        self.assertEqual(rel.domains(), {x1,x2,x11,x12})
        self.assertEqual({z.name for z in rel.targets()}, {z.name for z in {y1, y11, y2}})

        for dom in {x1, x11, x12}:
            [self.assertTrue(rel.between(dom, tar)) for tar in {y1, y11}]

        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))

        clonedOntology = ontology.clone()
        rel = clonedOntology.relations("rel")

        self.assertEqual({z.name for z in rel.domains()}, {z.name for z in {x1,x2,x11,x12}})
        self.assertEqual({z for z in rel.targets()}, {z.name for z in {y1, y11, y2}})

        for dom in {x1, x11, x12}:
            for tar in {y1, y11}:
                self.assertTrue(rel.between(dom, tar))

        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))


    def test_ontology_relation_differ(self):

        ontology = Language.ontology()

        relation = ontology.relations("informs")

        self.assertTrue(relation.between(ontology.concepts("Kieran"), ontology.concepts("Luke")))
        self.assertFalse(relation.between(ontology.concepts("Luke"), ontology.concepts("Luke")))

    def test_ontology_find_relation(self):

        ontology = Language.ontology()

        self.assertTrue(list(ontology.findRelations("Kieran", "Luke")))
        self.assertFalse(list(ontology.findRelations("Kieran", "Kieran")))

    def test_RelationConcept_order(self):
        """ Test whether adding a concept when the ontology is populated with
        dependant relations, correctly affects the correct relations. """

        # Get a relation from the ontology
        ontology = Language.ontology()
        rel_speaks = ontology.relations("speaks")

        # Steve doesn't exist within the ontology
        self.assertFalse("Steve" in rel_speaks.domains)
        self.assertFalse("Joe" in rel_speaks.domains)

        # Define concepts to be added
        steve = Concept("Steve", parents={"Person"}, category="static")
        joe  = Concept("Joe", parents={ontology.concepts("Person")}, category="static")
        ontology.concepts.add(steve)
        ontology.concepts.add(joe)

        # Assert that the concept has been updated
        self.assertTrue("Steve" in rel_speaks.domains)
        self.assertTrue("Joe" in rel_speaks.domains)

    def test_Relations(self):
        """ Ensure that relations that undergo changes within the ontology are
        reflected by future instances of the relation """

        # Get a relation from the ontology
        ontology = Language.ontology()
        rel_speaks = ontology.relations("speaks")

        # Steve doesn't exist within the ontology
        self.assertFalse(rel_speaks.between("Steve", "English"))

        # Define concepts to be added
        steve = Concept("Steve", parents={"Person"}, category="static")
        ontology.concepts.add(steve)

        # Assert that the concept has been updated
        self.assertTrue(rel_speaks.between("Steve", "English"))

    def test_findRelations(self):
        """ Ensure that the find relations finds the correct relations within the system when asked """

        ontology = Language.ontology()

        for relation in ontology.findRelations("Kieran", "English"):
            self.assertEqual(relation, ontology.relations("speaks"))

        for relation in ontology.findRelations("Kieran", "England"):
            self.assertIn(relation.name, ["born_in", "lives_in"])

    def test_LoadOntology_Concepts(self):
        """ Ensure that the process of loading an ontology from file is correct,
        that all concepts are created correctly and that the relations are all
        linked """

        ont = Language.ontology()

        # Ensure all concepts are loaded
        self.assertNotEqual(ont.concepts("Person"), None)
        self.assertNotEqual(ont.concepts("Kieran"), None)
        self.assertNotEqual(ont.concepts("Luke"), None)
        self.assertNotEqual(ont.concepts("Charlie"), None)

        self.assertNotEqual(ont.concepts("Language"), None)
        self.assertNotEqual(ont.concepts("English"), None)
        self.assertNotEqual(ont.concepts("German"), None)
        self.assertNotEqual(ont.concepts("French"), None)

        self.assertNotEqual(ont.concepts("Country"), None)
        self.assertNotEqual(ont.concepts("England"), None)
        self.assertNotEqual(ont.concepts("France"), None)
        self.assertNotEqual(ont.concepts("Germany"), None)

    def test_loadOntology_Concepts_textRepresentations(self):
        # Check that text representations are loaded correctly
        ont = Language.ontology()
        kieran = ont.concepts("Kieran")
        self.assertEqual(kieran.aliases, {"Legend", "Champ", "Badass"})

if __name__ == "__main__":
    unittest.main()
