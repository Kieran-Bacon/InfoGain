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

