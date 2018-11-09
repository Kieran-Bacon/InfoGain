import unittest

from infogain.knowledge import *
from infogain.cognition import InferenceEngine
from infogain.cognition.evalrule import EvalRule
from infogain.resources.ontologies import language

class Test_EvalRule(unittest.TestCase):

    def setUp(self):

        self.engine = InferenceEngine()

        self.con1, self.con2 = Concept("Con1"), Concept("Con2")
        self.inst1, self.inst2 = self.con1.instance(), self.con1.instance()

        self.engine.addConcept(self.con1)
        self.engine.addConcept(self.con2)

        self.conceptRule = EvalRule({self.con1}, {self.con2}, 100)
        self.instanceRule = EvalRule({self.inst1}, {self.inst2}, 80)

        self.conditionRule = EvalRule(self.con1, self.con2, 80, conditions=[
            Condition("100", 100)
        ])

    def test_hasCondition(self):

        # Assert that the condition does have rules to begin with
        self.assertTrue(self.conditionRule.hasConditions(self.inst1, self.inst2))

        # Evaluate something
        self.conditionRule.eval(self.inst1, self.inst2)

        # Assert that there are no conditions needed to be evaluated for this pairing
        self.assertFalse(self.conditionRule.hasConditions(self.inst1, self.inst2))

    def test_eval_with_invalid_instances_yields_0(self):
        self.assertEqual(self.conceptRule.eval(Instance(""), Instance("")), 0)
        self.assertEqual(self.instanceRule.eval(Instance(""), Instance("")), 0)
        self.assertEqual(self.conditionRule.eval(Instance(""), Instance("")), 0)

    def test_eval_on_facts(self):

        self.assertEqual(self.conceptRule.eval(self.inst1, self.inst2), 100)
        self.assertEqual(self.instanceRule.eval(self.inst1, self.inst2), 80)

    def test_eval_on_condition(self):
        self.assertEqual(self.conditionRule.eval(self.inst1, self.inst2), 80)

    def test_eval_when_lots_of_params(self):

        engine = InferenceEngine(ontology=language.ontology())

        self.assertEqual(engine.inferRelation(engine.instances("Kieran"), "speaks", engine.instances("English")), 100)


    def test_evalScenario(self):
        self.fail()

    def test_reset(self):

        self.test_hasCondition()

        self.conditionRule.reset()

        self.test_hasCondition()

    def test_instancesbehaveinthesamewayasconcepts(self):
        self.fail()