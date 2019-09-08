import unittest, pytest

from infogain.artefact import Document, Annotation
from infogain.cognition import InferenceEngine
from infogain.knowledge import Concept, Instance, Relation, Rule, Condition
from infogain.resources.ontologies import language

from infogain.exceptions import IncorrectLogic, ConsistencyError

class Test_InferenceEngine(unittest.TestCase):

    def test_addConcepts(self):
        """ Test that the adding of a new concept is done """

        engine = InferenceEngine()


        # Test the adding of an abstract concept to the inference engine
        engine.concepts.add(Concept("abstract", category="abstract"))

        self.assertIsNotNone(engine.concepts.get("abstract"))
        self.assertEqual(engine.instances("abstract"), set())  # Assert that there are no abstract instances

        # Test static adding
        static = Concept("static", category="static")
        engine.concepts.add(static)

        self.assertIsNotNone(engine.concepts.get("static"))
        self.assertEqual({static.instance()}, engine.instances("static"))  # Assert that static instance shall have one

        # Test dynamic adding
        dynamic = Concept("dynamic")
        engine.concepts.add(dynamic)

        self.assertIsNotNone(engine.concepts.get("dynamic"))
        self.assertEqual(engine.instances("dynamic"), set())

        engine.instances.add(dynamic.instance("first"))
        engine.instances.add(dynamic.instance("second", {"frequency": "60Hz"}))

        self.assertEqual({instance.name for instance in engine.instances("dynamic")}, {"first", "second"})

    def test_addRelation(self):

        engine = InferenceEngine()
        engine.concepts.add(Concept("x"))
        engine.concepts.add(Concept("y"))

        engine.relations.add(Relation("x", "simple", "y"))
        engine.relations.add(
            Relation("x", "soundlogic", "y", [Rule("x", "y", 100, conditions=[Condition("%", 100)])])
        )


        with pytest.raises(IncorrectLogic):
            engine.relations.add(
                Relation("x", "wrong", "y", [Rule("x", "y", 100, conditions=[Condition("graph()()", 100)])])
            )

    def test_addInstance(self):
        """ Add instances to the engine """

        dynamic = Concept("dynamic")
        static = Concept("static", category=Concept.STATIC)
        abstract = Concept("abstract", category=Concept.ABSTRACT)

        engine = InferenceEngine()
        for con in [dynamic, static, abstract]: engine.concepts.add(con)

        engine.instances.add(dynamic.instance())

        self.assertTrue(engine.instances("dynamic"), 1)

        instance = dynamic.instance()
        instance.properties["dynamic_prop"] = True

        engine.instances.add(instance)

        self.assertTrue(engine.instances("dynamic"), 2)

        for inst in engine.instances("dynamic"):
            if inst.name == instance.name:
                self.assertTrue(inst["dynamic_prop"])
                self.assertTrue(inst.dynamic_prop)

        with pytest.raises(ConsistencyError):
            engine.instances.add(Instance("Not a concept"))

        #TODO: Test for warning?
        engine.instances.add(static.instance())

        with pytest.raises(TypeError):
            # Type error as in trying to make an instance of an abstract concept - it is set off
            engine.instances.add(abstract.instance())

    def test_instances(self):
        """ Test the collection of instances """

        dynamic = Concept("dynamic")
        static = Concept("static", category=Concept.STATIC)
        abstract = Concept("abstract", category=Concept.ABSTRACT)

        engine = InferenceEngine()
        for con in [dynamic, static, abstract]: engine.concepts.add(con)

        self.assertEqual(static.instance(), engine.instances["static"])

    def test_inferRelation_no_conditions(self):

        engine = InferenceEngine()

        a, b = Concept("A", category="static"), Concept("B", category="static")
        atob = Relation({a}, "atob", {b})
        atob.rules.add(Rule(a, b, 45.0))

        assert(len(atob.rules) == 1)

        for con in [a, b]: engine.concepts.add(con)
        atob = engine.relations.add(atob)

        assert(len(atob.rules) == 1)

        self.assertAlmostEqual(engine.inferRelation(a.instance(), atob, b.instance()), 45.0)


    def test_inferRelation_conditions(self):
        engine = InferenceEngine()

        a, b = Concept("A", properties={"x": 10, "y": 15}, category="static"), Concept("B", category="static")
        atob = Relation({a}, "atob", {b})
        atob.rules.add(Rule(a, b, 45.0, conditions=[
            Condition("f(%.x, '(x == 10)*100')", 100.),
            Condition("f(%.y, '(y == 14)*100')", 50.)
        ]))

        for con in [a, b]: engine.concepts.add(con)
        engine.relations.add(atob)

        self.assertAlmostEqual(engine.inferRelation(a.instance(), atob, b.instance()), 22.5)

    def test_inferRelation_ignore_logic_conditions(self):

        engine = InferenceEngine()

        a, b = Concept("A", properties={"x": 10, "y": 15}, category="static"), Concept("B", category="static")
        atob = Relation({a}, "atob", {b})
        atob.rules.add(Rule(a, b, 55.0))
        atob.rules.add(Rule(a, b, 45.0, conditions=[
            Condition("f(%.x, '(x == 10)*100')", 100),
            Condition("f(%.y, '(y == 14)*100')",50)
        ]))

        for con in [a, b]: engine.concepts.add(con)
        engine.relations.add(atob)

        self.assertAlmostEqual(engine.inferRelation(a.instance(), atob, b.instance(), evaluate_conditions=False), 55.0)

    def test_addWorldKnowledge(self):

        engine = InferenceEngine(ontology=language.ontology())

        originalConfidence = engine.inferRelation(
            engine.concepts["Kieran"].instance(),
            "speaks",
            engine.concepts["English"].instance()
        )

        speaks = Annotation({
            "domain": {"concept": "Kieran", "text": "Kieran"},
            "relation": "speaks",
            "target": {"concept": "English", "text": "English"},

            "prediction": 1,
            "probability": 0.69
        })

        world_knowledge = Document()
        world_knowledge.Annotations([speaks])

        engine.addWorldKnowledge([world_knowledge])

        confidence = engine.inferRelation(
            engine.concepts["Kieran"].instance(),
            "speaks",
            engine.concepts["English"].instance()
        )

        # Ensure that the confidence relation has been affected by the world knowledge
        # Ensure that the confidence of the rules within the ontology are included
        self.assertEqual(confidence, (1 - (1-0.69)*(1-originalConfidence/100))*100)

    def test_worldKnowledge2(self):

        engine = InferenceEngine(ontology=language.ontology())

        lives_in = Annotation({
            "domain": {"concept": "Kieran", "text": "Kieran"},
            "relation": "lives_in",
            "target": {"concept": "Germany", "text": "Germany"},

            "prediction": 1,
            "probability": 0.69
        })

        doc = Document()
        doc.Annotations([lives_in])

        engine.addWorldKnowledge([doc])

        self.assertAlmostEqual(
            engine.inferRelation(
                engine.concepts["Kieran"].instance(),
                "lives_in",
                engine.concepts["Germany"].instance()
            ),
            69
        )

    def test_worldKnowledge3(self):

        engine = InferenceEngine(ontology=language.ontology())

        lives_in = Annotation({
            "domain": {"concept": "Kieran", "text": "Kieran"},
            "relation": "lives_in",
            "target": {"concept": "Germany", "text": "Germany"},

            "prediction": -1,
            "probability": 0.69
        })

        doc = Document()
        doc.Annotations([lives_in])

        engine.addWorldKnowledge([doc])

        self.assertAlmostEqual(
            engine.inferRelation(
                engine.concepts["Kieran"].instance(),
                "lives_in",
                engine.concepts["Germany"].instance()
            ),
            31
        )