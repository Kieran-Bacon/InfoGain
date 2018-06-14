import unittest, os, json

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Resources import Language


class Test_Ontology_Creation(unittest.TestCase):

    def setUp(self):
        self.person = Concept("Person", children={"Kieran"})
        self.kieran = Concept("Kieran", parents={self.person})

        self.language = Concept("Language", children={"English"})
        self.english = Concept("English", parents={self.language})

        self.speaks = Relation({self.person}, "speaks", {self.language})

    def test_load_and_save(self):

        ont, path = Language.ontology(get_path=True)
        ont.save(filename="tempOnt.json")
        
        with open("./tempOnt.json") as handler:
            file1_content = json.load(handler)

        with open(path) as handler:
            file2_content = json.load(handler)

                # TODO better comparison
        #self.assertEqual(file1_content, file2_content)

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

        self.assertEqual(ontology.relation("speaks"), {self.speaks})
        self.assertEqual(ontology.relation("placeholder"), None)

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

        relations = ontology.findRelations("Kieran", "English")

        for relation in ontology.relation("speaks"):
            for concept in relation.domains:
                print(concept)
            for concept in relation.targets:
                print(concept)

        self.assertEqual(ontology.relation("speaks"), set(relations))

        relations = ontology.findRelations("Kieran", "England")

        expected = ontology.relation("born_in").union(ontology.relation("lives_in"))

        self.assertEqual(expected, set(relations))

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
