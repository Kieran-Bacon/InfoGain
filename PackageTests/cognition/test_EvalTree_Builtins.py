import unittest

from infogain.artefact import Document, Datapoint
from infogain.knowledge import Concept, Instance, Relation

from infogain.cognition import InferenceEngine
from infogain.cognition import evaltrees

from infogain.resources.ontologies import language

class Test_EvalTreeBuiltins(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine(ontology=language.ontology())
        self.example = Concept("example", category="static")
        self.example2 = Concept("example2", category="static")

        self.factory = evaltrees.EvalTreeFactory(self.engine)

    def test_graph(self):
        
        logic = "graph(2, x + 2)"

        builtInFunction = self.factory.constructTree(logic)

        self.assertEqual(builtInFunction.eval(), 4)

    def test_is(self):

        logic = "is(%, @)"

        isNone = self.factory.constructTree(logic)

        inst = self.example.instance()
        inst2 = self.engine.concept("Kieran").instance()

        self.assertEqual(isNone.eval(scenario={"%": inst, "@": inst}), 100)
        self.assertEqual(isNone.eval(scenario={"%": inst, "@": inst2}), 0)

    def test_isNot(self):
        logic = "isNot(%, @)"

        isNot = self.factory.constructTree(logic)

        inst = self.example.instance()
        inst2 = self.engine.concept("Kieran").instance()

        self.assertEqual(isNot.eval(scenario={"%": inst, "@": inst}), 0)
        self.assertEqual(isNot.eval(scenario={"%": inst, "@": inst2}), 100)

    def test_facts(self):
        logic = "facts(#Kieran=lives_in=#England)"

        factNode = self.factory.constructTree(logic)

        inst = self.engine.concept("Kieran").instance()
        inst2 = self.engine.concept("England").instance()

        self.assertEqual(factNode.eval(scenario={"#Kieran": inst, "#England": inst2}), 50)

    def test_negative_facts(self):
        logic = "facts(#Kieran-lives_in-#Germany)"

        lives_in = Datapoint({
            "domain": {"concept": "Kieran", "text": "Kieran"},
            "relation": "lives_in",
            "target": {"concept": "Germany", "text": "Germany"},

            "prediction": 1,
            "probability": 0.69
        })

        doc = Document()
        doc.datapoints([lives_in])

        self.engine.addWorldKnowledge([doc])

        factsNode = self.factory.constructTree(logic)

        self.assertEqual(
            factsNode.eval(
                scenario={
                    "#Kieran": self.engine.concept("Kieran").instance(),
                    "#Germany": self.engine.concept("Germany").instance()
                }
            ),
            -69
        )

    def test_negative_facts2(self):
        logic = "facts(#Kieran-lives_in-#Germany)"

        lives_in = Datapoint({
            "domain": {"concept": "Kieran", "text": "Kieran"},
            "relation": "lives_in",
            "target": {"concept": "Germany", "text": "Germany"},

            "prediction": -1,
            "probability": 0.69
        })

        doc = Document()
        doc.datapoints([lives_in])

        self.engine.addWorldKnowledge([doc])

        factsNode = self.factory.constructTree(logic)

        self.assertEqual(
            factsNode.eval(
                scenario={
                    "#Kieran": self.engine.concept("Kieran").instance(),
                    "#Germany": self.engine.concept("Germany").instance()
                }
            ),
            69
        )
