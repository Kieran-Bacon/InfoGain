import unittest, pytest

from infogain.knowledge import Concept, Instance, Relation

from infogain.cognition import InferenceEngine
from infogain.cognition.evaltrees import EvalTreeFactory
from infogain.cognition.treenodes.conceptnode import ConceptNode

class Test_PropertyNode(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine()

        self.example = Concept("example", category="static")
        self.example.properties["age"] = 24
        self.engine.addConcept(self.example)

        self.maps_to = Relation({self.example}, "maps_to", {self.example})
        self.engine.addRelation(self.maps_to)

        self.scenario = {"#example": self.example.instance()}

        self.factory = EvalTreeFactory(self.engine)

    def test_get_property(self):

        for logic, answer in {
            "#example.age": 24
            }.items():

            node = self.factory.constructTree(logic)

            self.assertEqual(
                node.eval(
                    scenario = {
                        "#example": self.example.instance(),
                    }
                ),
                answer
            )