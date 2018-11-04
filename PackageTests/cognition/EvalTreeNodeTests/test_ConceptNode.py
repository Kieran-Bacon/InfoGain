import unittest

from infogain.knowledge import Concept, Instance, Relation

from infogain.cognition import InferenceEngine
from infogain.cognition.evaltrees import EvalTreeFactory
from infogain.cognition.treenodes.conceptnode import ConceptNode

class Test_ConceptNode(unittest.TestCase):
    
    def setUp(self):

        self.engine = InferenceEngine()

        self.example = Concept("example", category="static")
        self.example.properties["age"] = 24
        self.engine.addConcept(self.example)

        self.maps_to = Relation({self.example}, "maps_to", {self.example})
        self.engine.addRelation(self.maps_to)

        self.scenario = {"#example": self.example.instance()}

        self.factory = EvalTreeFactory(self.engine)

    def test_ConceptNodeCreation(self):

        conceptPatterns = [
            "#example",
            "%",
            "@",
            "#[something]example",
            "#examplecall()"
        ]

        for logic in conceptPatterns:
            node = self.factory.constructTree(logic)  # Generate node
            self.assertTrue(isinstance(node, ConceptNode))  # Check that the node is the concept node

    def test_node_functions(self):
        logic = "#example"

        conceptNode = self.factory.constructTree(logic)

        self.assertEqual(str(conceptNode), logic)
        self.assertEqual(conceptNode.parameters(), {"#example"})
        self.assertEqual(conceptNode.eval(scenario=self.scenario), 100)
        self.assertEqual(conceptNode.instance(scenario=self.scenario).concept, self.example)

        logic = "#[thebest]example"

        node = self.factory.constructTree(logic)

        self.assertEqual(node.parameters(), {logic})

    def test_nodes_parameters_join_correctly(self):

        logic = "f(#[0]example, #[1]example, #[0]example, #example, 100)"

        node = self.factory.constructTree(logic)

        self.assertEqual(node.parameters(), {"#[0]example", "#[1]example", "#example"})

    def test_instance_calling(self):
        """ Test that a concept node that represents a concept with an instance with its call overloaded works correctly
        in the logic. That the instance's call function is checked and evaluated and that the answer makes sense """


        class exampleInst(Instance):
            def __call__(self, number):
                return number*2

        self.example.setInstanceClass(exampleInst)

        conceptPatterns = [
            "%(20)",
            "@(20)",
            "#example(20)",
            "#[something]example(20)"
        ]

        for logic in conceptPatterns:
            node = self.factory.constructTree(logic)
            scenario = {logic[:logic.index("(")]: self.example.instance()}
            self.assertEqual(node.eval(scenario = scenario), 40)