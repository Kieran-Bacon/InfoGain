import unittest, pytest

from infogain.knowledge import Concept, Instance, Relation
from infogain.exceptions import IncorrectLogic

from infogain.cognition import InferenceEngine
from infogain.cognition import evaltrees
from infogain.cognition.treenodes import StringNode

class Test_eval_trees(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine()

        self.example = Concept("example", category="static")
        self.example.properties["age"] = 24
        self.engine.concepts.add(self.example)

        self.maps_to = Relation({self.example}, "maps_to", {self.example})
        self.engine.addRelation(self.maps_to)

        self.scenario = {"#example": self.example.instance()}

        self.factory = evaltrees.EvalTreeFactory(self.engine)

    def test_ConceptNode_functions(self):

        logic = "#example"

        conceptNode = self.factory.constructTree(logic)

        self.assertEqual(str(conceptNode), logic)
        self.assertEqual(conceptNode.parameters(), {"#example"})
        self.assertEqual(conceptNode.eval(scenario=self.scenario), 100)
        self.assertEqual(conceptNode.instance(scenario=self.scenario).concept, self.example)

    def test_FunctionNode_functions(self):

        class exampleInstance(Instance):

            def function(self):
                return "function returned value"

            def function_with_arguments(self, x, y, z):
                return x + y + z

        self.example.setInstanceClass(exampleInstance)

        inst = self.example.instance()
        scenario = {"#example": inst}

        logic = "#example.function()"

        functionNode = self.factory.constructTree(logic)

        self.assertEqual(str(functionNode), logic)
        self.assertEqual(functionNode.eval(scenario=scenario), "function returned value")
        self.assertEqual(functionNode.parameters(), {"#example"})

        logic2 = "#example.function_with_arguments(1,3,4)"

        functionNode = self.factory.constructTree(logic2)

        self.assertEqual(str(functionNode), logic2)
        self.assertEqual(functionNode.eval(scenario=scenario), 8)
        self.assertEqual(functionNode.parameters(), {"#example"})

        logic3 = "#example.function_with_arguments(#example.age,3,4)"

        functionNode = self.factory.constructTree(logic3)

        self.assertEqual(functionNode.eval(scenario=scenario), 31)

    def test_RelationNode_function(self):

        logic = "#example=maps_to=#example"

        relationNode = self.factory.constructTree(logic)

        self.assertEqual(str(relationNode), logic)
        self.assertEqual(relationNode.parameters(), {"#example"})
        self.assertEqual(relationNode.eval(scenario=self.scenario), 0)

    def test_PropertyNode_function(self):
        """ Test that the extraction of a concept property """

        logic = "#example.age"
        broken = "#example.broken"

        propertyNode = self.factory.constructTree(logic)
        brokenNode = self.factory.constructTree(broken)

        self.assertEqual(str(propertyNode), logic)
        self.assertEqual(propertyNode.parameters(), {"#example"})
        self.assertEqual(propertyNode.eval(scenario=self.scenario), 24)
        self.assertEqual(brokenNode.eval(scenario=self.scenario), None)

    def test_primatives(self):

        with pytest.raises(IncorrectLogic):
            self.factory.constructTree("Hello there")

        self.assertEqual(StringNode("Hello there").eval(), "Hello there")
        self.assertEqual(self.factory.constructTree("128.2").eval(), 128.2)
        self.assertEqual(self.factory.constructTree("128").eval(), 128)


    def test_long_logic(self):


        logic = "f(#example=maps_to=#example, 400,#example.age,'x + y + z')"

        tree = self.factory.constructTree(logic)

        self.assertEqual(tree.eval(scenario=self.scenario), 424.0)

