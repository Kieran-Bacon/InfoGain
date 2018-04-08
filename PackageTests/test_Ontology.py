import unittest

from . import LANGUAGE_ONTOLOGY

from InfoGain import Ontology, Concept, Relation

class Test_Ontology_Creation(unittest.TestCase):

    def setUp(self):
        self.person = Concept("Person")
        self.kieran = Concept("Kieran")

        self.language = Concept("Language")
        self.english = Concept("English")

        self.person.addChild(self.kieran)
        self.kieran.addParent(self.person)

        self.language.addChild(self.english)
        self.english.addParent(self.language)

        self.speaks = Relation({self.person}, "speaks", {self.language})

    def test_Concepts_Ontology(self):

        ontology = Ontology("Sample")

        ontology.addConcept(self.person)
        ontology.addConcept(self.kieran)

        self.assertEqual(ontology.concept("Person"), self.person)
        self.assertEqual(ontology.concept("Kieran"), self.kieran)
        self.assertEqual(ontology.concept("Dave"), None)

    def test_Relations_Ontology(self):

        ontology = Ontology("Sample")
        ontology.addRelation(self.speaks)

        self.assertEqual(ontology.relation("speaks"), self.speaks)
        self.assertEqual(ontology.relation("placeholder"), None)

    def test_RelationConcept_order(self):
        """ Test whether adding a concept when the ontology is populated with 
        dependant relations, correctly affects the correct relations. """
        pass

    def test_Relations(self):
        """ Ensure that relations that undergo changes within the ontology are
        reflected by future instances of the relation """
        pass

    def test_LoadOntology_Concepts(self):
        """ Ensure that the process of loading an ontology from file is correct,
        that all concepts are created correctly and that the relations are all 
        linked """

        ont = Ontology(filepath=LANGUAGE_ONTOLOGY)

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

        # Check that text representations are loaded correctly
        conceptKieran = ont.concept("Kieran")
        self.assertEqual(conceptKieran.textRepr(),{"Legend", "Champ","Badass"})

    def test_familyTree_Concepts(self):
        raise NotImplementedError()

if __name__ == "__main__":
    unittest.main()