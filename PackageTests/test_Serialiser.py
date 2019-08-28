import os
import unittest

import infogain
from infogain.knowledge import Concept, Relation, Rule, Condition

class Test_SerialiserFactory(unittest.TestCase):
    """ Test that the Serialiser Factory behaves as expected """

    @classmethod
    def setUpClass(cls):
        cls.path = './serialised.json'

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)

    def setUp(self):
        """ Define a basic ontology to save and load """

        ontology = infogain.knowledge.Ontology()

        # Generate the concepts
        a, b, c = Concept("A"), Concept("B", parents={"A"}), Concept("C", parents={"B"})
        x, y, z = Concept("X"), Concept("Y", parents={"X"}), Concept("Z", parents={"Y"})

        # Generate a relationship
        a_x = Relation({a}, "to", {x}, rules=[
            Rule(b, y, 100)
        ])

        for concept in (a,b,c,x,y,z,):
            ontology.concepts.add(concept)

        ontology.relations.add(a_x)
        self.ontology = ontology

    def test_JsonEncoder(self):

        jsonSerialiser = infogain.Serialiser("json")

        jsonSerialiser.save(self.ontology, self.path)

        loadedOntology = jsonSerialiser.load(self.path)

        for concept in self.ontology.concepts():
            loadedConcept = loadedOntology.concepts[concept.name]

            self.assertEqual(set(con.name for con in concept.parents), set(con.name for con in loadedConcept.parents))
            self.assertEqual(set(con.name for con in concept.children), set(con.name for con in loadedConcept.children))

        for relation in self.ontology.relations():
            loadedRelation = loadedOntology.relations[relation.name]

            for group_1, group_2 in zip(relation.domains, loadedRelation.domains):
                self.assertEqual(set(con.name for con in group_1), set(con.name for con in group_2))

            for group_1, group_2 in zip(relation.targets, loadedRelation.targets):
                self.assertEqual(set(con.name for con in group_1), set(con.name for con in group_2))

            for rule, loaded in zip(relation.rules, loadedRelation.rules):
                self.assertEqual(rule.domains.toStringSet(), loaded.domains.toStringSet())
                self.assertEqual(rule.targets.toStringSet(), loaded.targets.toStringSet())

                self.assertEqual(rule.confidence, loaded.confidence)


