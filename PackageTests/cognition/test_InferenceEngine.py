import unittest, pytest

from infogain.cognition import InferenceEngine
from infogain.knowledge import Concept, ConceptInstance, Relation, Rule
from infogain.exceptions import IncorrectLogic

class Test_InferenceEngine(unittest.TestCase):

    def test_addConcept(self):
        """ Test that the adding of a new concept is done """

        engine = InferenceEngine()
        
        # Test abstract adding
        instanceCollection = engine._conceptInstances.copy()

        engine.addConcept(Concept("abstract", category="abstract"))

        self.assertIsNotNone(engine.concept("abstract"))
        self.assertEqual(engine._conceptInstances, instanceCollection) # No change

        # Test static adding
        static = Concept("static", category="static")
        engine.addConcept(static)

        self.assertIsNotNone(engine.concept("static"))
        self.assertEqual(static.instance(), engine.instances("static"))

        # Test dynamic adding
        dynamic = Concept("dynamic")
        engine.addConcept(dynamic)

        self.assertIsNotNone(engine.concept("dynamic"))
        self.assertEqual(engine.instances("dynamic"), [])

        # Test that the collection has been generated correctly
        self.assertEqual(engine._conceptInstances.keys(), {"static", "dynamic"})

    def test_addRelation(self):

        engine = InferenceEngine()
        engine.addConcept(Concept("x"))
        engine.addConcept(Concept("y"))

        engine.addRelation(Relation("x", "simple", "y"))
        engine.addRelation(Relation("x", "soundlogic", "y", [Rule("x", "y", 100, [{"logic": "%", "salience": 100}])]))
        

        with pytest.raises(IncorrectLogic):
            engine.addRelation(Relation("x", "wrong", "y", [Rule("x", "y", 100, [{"logic": "graph()()", "salience": 100}])]))

    def test_addInstance(self):
        self.fail("Not implemented")

    def test_instances(self):
        self.fail("Not implemented")

    def test_inferRelation(self):
        self.fail("Not implemented")

    def test_addWorldKnowledge(self):
        self.fail("Not implemented")