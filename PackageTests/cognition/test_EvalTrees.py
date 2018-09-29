import unittest

from infogain.knowledge import Concept, Relation

from infogain.cognition import InferenceEngine, ConceptInstance
from infogain.cognition import evaltrees

class Test_eval_trees(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine()

        self.example = Concept("example", category="static")
        self.example.properties["age"] = 24
        self.engine.addConcept(self.example)

        self.maps_to = Relation({self.example}, "maps_to", {self.example})
        self.engine.addRelation(self.maps_to)

        self.scenario = {"#example": self.engine.instances("example")[0]}

        self.factory = evaltrees.EvalTreeFactory(self.engine)

    def test_ConceptNode_functions(self):

        logic = "#example"

        conceptNode = self.factory.constructTree(logic)

        self.assertEqual(str(conceptNode), logic)
        self.assertEqual(conceptNode.parameters(), {"#example"})
        self.assertEqual(conceptNode.eval(scenario=self.scenario), 100)
        self.assertEqual(conceptNode.instance(scenario=self.scenario), self.example)

    def test_FunctionNode_functions(self):

        def function():
            return "function returned value"

        def function_with_arguments(x, y, z):
            return x + y + z

        inst = self.engine.instances("example")[0]
        inst.addFunction(function)
        inst.addFunction(function_with_arguments)

        logic = "#example>function()"
    
        functionNode = self.factory.constructTree(logic)

        self.assertEqual(str(functionNode), logic)
        self.assertEqual(functionNode.eval(scenario=self.scenario), "function returned value")
        self.assertEqual(functionNode.parameters(), {"#example"})

        logic2 = "#example>function_with_arguments(1,3,4)"

        functionNode = self.factory.constructTree(logic2)        

        self.assertEqual(str(functionNode), logic2)
        self.assertEqual(functionNode.eval(scenario=self.scenario), 8)
        self.assertEqual(functionNode.parameters(), {"#example"})

        logic3 = "#example>function_with_arguments(#example.age,3,4)"

        functionNode = self.factory.constructTree(logic3)

        self.assertEqual(functionNode.eval(scenario=self.scenario), 31)

    def test_RelationNode_function(self):

        logic = "#example=maps_to=#example"

        relationNode = self.factory.constructTree(logic)

        self.assertEqual(str(relationNode), logic)
        self.assertEqual(relationNode.parameters(), {"#example"})
        self.assertEqual(relationNode.eval(scenario=self.scenario), 0)

    def test_BuiltInFunctionNode_function(self):
        
        logic = "graph(2, x + 2)"

        builtInFunction = self.factory.constructTree(logic)

        self.assertEqual(builtInFunction.eval(), 4)


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

        self.assertEqual(self.factory.constructTree("Hello there").eval(), "Hello there")
        self.assertEqual(self.factory.constructTree("128.2").eval(), 128.2)
        self.assertEqual(self.factory.constructTree("128").eval(), 128)


    def test_long_logic(self):


        logic = "graph(#example=maps_to=#example, 400,#example.age,x + y + z)"

        tree = self.factory.constructTree(logic)

        self.assertEqual(tree.eval(scenario=self.scenario), 424.0)

