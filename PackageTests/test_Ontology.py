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

    def test_loadOntology_Concepts_textRepresentations(self):
        # Check that text representations are loaded correctly
        ont = Ontology(filepath=LANGUAGE_ONTOLOGY)
        kieran = ont.concept("Kieran")
        self.assertEqual(kieran.textRepr(), {"Legend", "Champ", "Badass"})

    def test_familyTree_Concepts(self):

        ont = Ontology(filepath=LANGUAGE_ONTOLOGY)

        person = ont.concept("Person")
        kieran = ont.concept("Kieran")
        sadKieran = ont.concept("Sad_Kieran")

        self.assertTrue(person.isAncestorOf(kieran))
        self.assertTrue(person.isParentOf(kieran))
        self.assertTrue(kieran.isChildOf(person))
        self.assertTrue(kieran.isDecendantOf(person))

        self.assertTrue(person.isAncestorOf(sadKieran))
        self.assertFalse(person.isParentOf(sadKieran))
        self.assertFalse(sadKieran.isChildOf(person))
        self.assertTrue(sadKieran.isDecendantOf(person))

    def test_conceptText(self):
        ont = Ontology(filepath=LANGUAGE_ONTOLOGY)

        expectedRepr = {'Badass': 'Kieran',
                        'Champ': 'Kieran',
                        'Charlie': 'Charlie',
                        'Country': 'Country',
                        'England': 'England',
                        'English': 'English',
                        'France': 'France',
                        'French': 'French',
                        'German': 'German',
                        'Germany': 'Germany',
                        'Kieran': 'Kieran',
                        'Language': 'Language',
                        'Legend': 'Kieran',
                        'Luke': 'Luke',
                        'Person': 'Person',
                        'Sad_Kieran': 'Sad_Kieran',
                        'Spanish': 'Spanish',
                        'Spain':'Spain'}

        self.assertEqual(ont.conceptText(), expectedRepr)


if __name__ == "__main__":
    unittest.main()
