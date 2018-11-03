import unittest

from infogain.knowledge import *
from infogain.cognition import InferenceEngine
from infogain.cognition.evalrule import EvalRule

class Test_EvalRule(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine()

        self.con1 = Concept("Con1")
        self.con2 = Concept("Con2")

        self.engine.addConcept(self.con1)
        self.engine.addConcept(self.con2)

        self.conceptRule = EvalRule({self.con1}, {self.con2}, 100)
        self.instanceRule = EvalRule({self.con1.instance()}, {self.con2.instance()}, 80)

    def test_assigningOntology(self):
        self.fail()

    def test_hasCondition(self):
        self.fail()

    def test_eval(self):
        self.fail()

    def test_evalScenario(self):
        self.fail()

    def test_reset(self):
        self.fail()

    def test_evalIdGen(self):
        self.fail()

    def test_instancesbehaveinthesamewayasconcepts(self):
        self.fail()