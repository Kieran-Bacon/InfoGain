import unittest, pytest
from infogain import knowledge
from infogain.knowledge import Concept
from infogain.knowledge.rule import RuleConceptSet, ConditionManager

class Test_Rule(unittest.TestCase):

    def setUp(self):
        """ Concepts that form a complex structure of layers within an ontology - In a "W I" formation

            A   E   I   J
             B D F H    K
              C   G     L

        """

        # Top row
        self.a, self.e, self.i, self.j = Concept("A"), Concept("E"), Concept("I"), Concept("J")

        # Middle row
        self.b, self.d  = Concept("B", parents={self.a}), Concept("D", parents={self.e})
        self.f, self.h = Concept("F", parents={self.e}), Concept("H", parents={self.i})
        self.k = Concept("K", parents={self.j})

        # Bottom row
        self.c, self.g = Concept("C", parents={self.b, self.d}), Concept("G", parents={self.f, self.h})
        self.l = Concept("L", parents={self.k})

    def test_domains_targets_with_no_conditions(self):
        """ Test that creating a rule with no conditions results in a rule that has as domains and targets, only the
        concepts passed at initialisation
        """

        rule = knowledge.Rule({self.b, self.d}, self.k, 80)

        self.assertEqual(rule.domains, {self.b, self.d, self.c})
        self.assertEqual(rule.targets, {self.k, self.j})

    def test_subscription_with_no_conditions(self):
        """ Assert that when there are no conditions for the rule, that no concepts can subscribe to the rule """

        rule = knowledge.Rule(self.h, self.k, 20)

        rule.subscribe(self.i)
        rule.subscribe(self.a)
        rule.subscribe(self.l)

        self.assertEqual(rule.domains, {self.h, self.g})
        self.assertEqual(rule.targets, {self.k, self.j})

        g1 = Concept("G1", parents={self.g})
        jStar = Concept("J*", children={self.j})

        rule.subscribe(g1)
        rule.subscribe(jStar)

        self.assertEqual(rule.domains, {self.h, self.g, g1})
        self.assertEqual(rule.targets, {self.k, self.j, jStar})

    def test_applies_with_no_conditions(self):
        """ Assert that a rule only applies to domains and targets (and their instances) of the Rule """

        rule = knowledge.Rule(self.k, self.g, 100)

        self.assertTrue(rule.applies(self.k, self.g))
        self.assertTrue(rule.applies(self.k.instance(), self.g.instance()))
        self.assertFalse(rule.applies(self.g, self.k))
        self.assertFalse(rule.applies(self.j, self.h))

    def test_conditions_with_no_conditions(self):
        """ Test that the conditions have the values we would expect from them given that they aren't present... """

        rule = knowledge.Rule(self.k, self.g, 50)

        self.assertFalse(rule.conditions)
        for _ in rule.conditions:
            self.fail("There were apparently conditions when there shouldn't have been")

        self.assertFalse(rule.conditions.isConditionOnTarget())

    def test_conditions_order(self):
        """ Test that the order of the conditions is in line with their salience """

        rule = knowledge.Rule(
            self.k,
            self.g,
            100,
            conditions = [
                knowledge.Condition("10", salience=67),
                knowledge.Condition("199", salience=99),
                knowledge.Condition("asd", salience=70),
                knowledge.Condition("sda", salience=40)
            ]
        )

        for condition, salience in zip(rule.conditions, [99, 70, 67, 40]):
            self.assertEqual(condition.salience, salience)

    def test_domains_targets_with_conditions_conditional_on_target(self):

        rule = knowledge.Rule({self.b, self.d}, self.k, 80, conditions=[knowledge.Condition("@", 100)])

        self.assertEqual(rule.domains, {self.b, self.d, self.c})
        self.assertEqual(rule.targets, {self.k, self.j, self.l})

    def test_subscribe_with_conditions_conditional_on_target(self):
        rule = knowledge.Rule(self.h, self.k, 20, conditions=[knowledge.Condition("@", 100)])

        rule.subscribe(self.i)
        rule.subscribe(self.a)

        self.assertEqual(rule.domains, {self.h, self.g})
        self.assertEqual(rule.targets, {self.k, self.j, self.l})

        g1 = Concept("G1", parents={self.g})
        jStar = Concept("J*", children={self.j})
        l1 = Concept("L1", parents={self.l})

        rule.subscribe(g1)
        rule.subscribe(jStar)
        rule.subscribe(l1)

        self.assertEqual(rule.domains, {self.h, self.g, g1})
        self.assertEqual(rule.targets, {self.k, self.l, self.j, jStar, l1})

    def test_applies_with_conditions_conditional_on_target(self):

        rule = knowledge.Rule({self.b, self.d}, self.k, 80, conditions=[knowledge.Condition("@", 100)])


        self.assertTrue(rule.applies(self.b, self.k))
        self.assertTrue(rule.applies(self.c, self.j))

class Test_RelationConceptSet(unittest.TestCase):

    def test_failed(self):
        self.fail()

class Test_ConditionManager(unittest.TestCase):

    def test_failed(self):
        self.fail()

if __name__ == "__main__":
    unittest.main()