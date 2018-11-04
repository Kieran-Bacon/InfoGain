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
        
        logic = "f(2, x + 2)"

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

    def test_equality(self):
        """ Test that two instances are the same instance """

        self.assertEqual(self.factory.constructTree("eq(10.0, 10)").eval(), 100)
        self.assertEqual(self.factory.constructTree("eq(10.1, 10)").eval(), 0)

        self.assertEqual(self.factory.constructTree("eq('Hello world', 'Hello world')").eval(), 100)
        self.assertEqual(self.factory.constructTree("eq('Hello world', 'Hello world!')").eval(), 0)
        self.assertEqual(self.factory.constructTree("eq(Hello world, 'Hello world')").eval(), 100)
        self.assertEqual(self.factory.constructTree("eq('Hello world', Hello world)").eval(), 0)

    def test_notequality(self):
        """ Test that two instances are the same instance """

        self.assertEqual(self.factory.constructTree("eqNot(10.0, 10)").eval(), 0)
        self.assertEqual(self.factory.constructTree("eqNot(10.1, 10)").eval(), 100)

        self.assertEqual(self.factory.constructTree("eqNot('Hello world', 'Hello world')").eval(), 0)
        self.assertEqual(self.factory.constructTree("eqNot('Hello world', 'Hello world!')").eval(), 100)
        self.assertEqual(self.factory.constructTree("eqNot(Hello world, 'Hello world')").eval(), 0)
        self.assertEqual(self.factory.constructTree("eqNot('Hello world', Hello world)").eval(), 100)

    def test_approx(self):

        self.assertEqual(self.factory.constructTree("approx(10.0, 10, 1)").eval(), 100)
        self.assertAlmostEqual(self.factory.constructTree("approx(10.1, 10, 1)").eval(), 90)

    def test_approximate_time_builtin(self):


        return
        import datetime

        engine = InferenceEngine()
        engine.importBuiltin("time")

        example = Concept("example", category="static")
        example.properties["date"] = datetime.datetime.strptime("18-09-19", "%d-%m-%Y")
        example.properties["date"] = engine.concept("datetime").instance("18.09.19")


        engine.addConcept(Concept())

        logic = "@period>length(12.08.19, #example.date), "

        logic = "eq(#example.date, @date>date(18.09.19))"

        logic = "@date.before(18.09.19, #example>birthday)"

        logic = "@period(17.09.2001, #example.birthday)>length()"