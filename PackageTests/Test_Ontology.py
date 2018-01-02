import unittest

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

    def test_Ontology_files(self):
        """ Ensure that the process of loading an ontology from file is correct,
        that all concepts are created correctly and that the relations are all 
        linked """

if __name__ == "__main__":
    unittest.main()