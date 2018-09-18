import unittest, os, json

from infogain.knowledge import Ontology, Concept, Relation
from infogain.resources.ontologies import language as Language


class Test_Ontology_Creation(unittest.TestCase):

    def setUp(self):
        self.person = Concept("Person", children={"Kieran"})
        self.kieran = Concept("Kieran", parents={self.person})

        self.language = Concept("Language", children={"English"})
        self.english = Concept("English", parents={self.language})

        self.speaks = Relation({self.person}, "speaks", {self.language})

        self.maxDiff = None

    def test_load_and_save(self):
        """ Test that saving and ontology returns it to the same state as it was before """

        ont, path = Language.ontology(get_path=True)

        with open(path, "r") as handler:
            content = handler.read()

        self.assertEqual(content, ont.toJson())

    def test_Concepts_Ontology(self):

        ontology = Ontology("Sample")

        ontology.addConcept(self.kieran)
        ontology.addConcept(self.person)

        self.assertEqual(ontology.concept("Person"), self.person)
        self.assertEqual(ontology.concept("Kieran"), self.kieran)
        self.assertEqual(ontology.concept("Dave"), None)

    def test_Relations_Ontology(self):

        ontology = Ontology("Sample")
    
        for concept in [self.kieran, self.person, self.english, self.language]:
            ontology.addConcept(concept)

        ontology.addRelation(self.speaks)

        self.assertEqual(ontology.relation("speaks"), self.speaks)
        self.assertEqual(ontology.relation("placeholder"), None)

    def test_Relations_Clone_Ontology(self):

        ontology = Ontology("Test1")

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})

        for con in [x,x1,x11,x12,x2,y,y1,y2,y11]:
            ontology.addConcept(con)

        rel = Relation([[x1], [x2]], "rel", [[y1], [y2]])

        ontology.addRelation(rel)

        self.assertEqual(rel.domains, {x1,x2,x11,x12})
        self.assertEqual({z.name for z in rel.targets}, {z.name for z in {y1, y11, y2}})

        for dom in {x1, x11, x12}:
            [self.assertTrue(rel.between(dom, tar)) for tar in {y1, y11}]

        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))

        clonedOntology = ontology.clone()
        rel = clonedOntology.relation("rel")
        
        self.assertEqual({z.name for z in rel.domains}, {z.name for z in {x1,x2,x11,x12}})
        self.assertEqual({z for z in rel.targets}, {z.name for z in {y1, y11, y2}})

        print(rel._between)

        for dom in {x1, x11, x12}:
            for tar in {y1, y11}:
                self.assertTrue(rel.between(dom, tar))
    
        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))


    def test_ontology_relation_differ(self):

        ontology = Language.ontology()

        relation = ontology.relation("informs")

        self.assertTrue(relation.between(ontology.concept("Kieran"), ontology.concept("Luke")))
        self.assertFalse(relation.between(ontology.concept("Luke"), ontology.concept("Luke")))

    def test_ontology_find_relation(self):

        ontology = Language.ontology()

        self.assertTrue(list(ontology.findRelations("Kieran", "Luke")))
        self.assertFalse(list(ontology.findRelations("Kieran", "Kieran")))

    def test_RelationConcept_order(self):
        """ Test whether adding a concept when the ontology is populated with 
        dependant relations, correctly affects the correct relations. """
        pass

    def test_Relations(self):
        """ Ensure that relations that undergo changes within the ontology are
        reflected by future instances of the relation """
        pass

    def test_findRelations(self):
        """ Ensure that the find relations finds the correct relations within the system when asked """

        ontology = Language.ontology()

        for relation in ontology.findRelations("Kieran", "English"):
            self.assertEqual(relation, ontology.relation("speaks"))

        for relation in ontology.findRelations("Kieran", "England"):
            self.assertIn(relation.name, ["born_in", "lives_in"])

    def test_LoadOntology_Concepts(self):
        """ Ensure that the process of loading an ontology from file is correct,
        that all concepts are created correctly and that the relations are all 
        linked """

        ont = Language.ontology()

        # Ensure all concepts are loaded
        self.assertNotEqual(ont.concept("Person"), None)
        self.assertNotEqual(ont.concept("Kieran"), None)
        self.assertNotEqual(ont.concept("Luke"), None)
        self.assertNotEqual(ont.concept("Charlie"), None)

        self.assertNotEqual(ont.concept("Language"), None)
        self.assertNotEqual(ont.concept("English"), None)
        self.assertNotEqual(ont.concept("German"), None)
        self.assertNotEqual(ont.concept("French"), None)

        self.assertNotEqual(ont.concept("Country"), None)
        self.assertNotEqual(ont.concept("England"), None)
        self.assertNotEqual(ont.concept("France"), None)
        self.assertNotEqual(ont.concept("Germany"), None)

    def test_loadOntology_Concepts_textRepresentations(self):
        # Check that text representations are loaded correctly
        ont = Language.ontology()
        kieran = ont.concept("Kieran")
        self.assertEqual(kieran.alias, {"Legend", "Champ", "Badass"})

    def test_ontology_clone(self):
        ont, path = Language.ontology(get_path=True )

        cloned = ont.clone()

        cloned.save(filename="tempOnt.json")

        with open("./tempOnt.json") as handler:
            file1_content = json.load(handler)

        with open(path) as handler:
            file2_content = json.load(handler)

        # TODO better comparison
        #self.assertEqual(file1_content, file2_content)

        os.remove("tempOnt.json")

    def test_ontology_pickle_able(self):
        import pickle
        ont = pickle.loads(pickle.dumps(Language.ontology()))
        self.assertTrue(ont.concept("Kieran") is not None)
        self.assertEqual(ont.concept("Kieran"), Language.ontology().concept("Kieran"))

if __name__ == "__main__":
    unittest.main()
