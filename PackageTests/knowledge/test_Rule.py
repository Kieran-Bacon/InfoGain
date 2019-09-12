import unittest, pytest
from infogain import knowledge
from infogain.knowledge import Concept, Relation, Rule, Condition

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

        rule = knowledge.Rule({self.b, self.d}, self.k, .8)

        self.assertEqual(rule.domains, {self.b, self.d, self.c})
        self.assertEqual(rule.targets, {self.k, self.j})

    def test_applies_with_no_conditions(self):
        """ Assert that a rule only applies to domains and targets (and their instances) of the Rule """

        rule = knowledge.Rule(self.k, self.g)

        self.assertTrue(rule.applies(self.k, self.g))
        self.assertTrue(rule.applies(self.k.instance(), self.g.instance()))
        self.assertFalse(rule.applies(self.g, self.k))
        self.assertFalse(rule.applies(self.j, self.h))

    def test_conditions_with_no_conditions(self):
        """ Test that the conditions have the values we would expect from them given that they aren't present... """

        rule = knowledge.Rule(self.k, self.g, .5)

        self.assertFalse(rule.conditions)
        for _ in rule.conditions:
            self.fail("There were apparently conditions when there shouldn't have been")

        self.assertFalse(rule.conditions.isConditionalOnTarget())

    def test_conditions_order(self):
        """ Test that the order of the conditions is in line with their salience """

        rule = knowledge.Rule(
            self.k,
            self.g,
            conditions = [
                knowledge.Condition("10", salience=.67),
                knowledge.Condition("199", salience=.99),
                knowledge.Condition("asd", salience=.70),
                knowledge.Condition("sda", salience=.40)
            ]
        )

        for condition, salience in zip(rule.conditions, [.99, .70, .67, .40]):
            self.assertEqual(condition.salience, salience)

    def test_domains_targets_with_conditions_conditional_on_target(self):

        rule = knowledge.Rule({self.b, self.d}, self.k, .80, conditions=[knowledge.Condition("@", .100)])

        self.assertEqual(rule.domains, {self.b, self.d, self.c})
        self.assertEqual(rule.targets, {self.k, self.j, self.l})

    def test_applies_with_conditions_conditional_on_target(self):

        rule = knowledge.Rule({self.b, self.d}, self.k, .80, conditions=[knowledge.Condition("@", .100)])


        self.assertTrue(rule.applies(self.b, self.k))
        self.assertTrue(rule.applies(self.c, self.j))

class Test_RelationConceptSet(unittest.TestCase):

    def setUp(self):

        self.domain = Concept("Domain")
        self.target = Concept("Target")

        self.a = Concept("A")
        self.b = Concept("B", parents={self.a})
        self.c = Concept("C", parents={self.b})

        self.x = Concept("X")
        self.y = Concept("Y", parents={self.x})
        self.z = Concept("Z", parents={self.y})

        self.relation = Relation({self.a}, "example", {self.x})

    def test_add(self):

        rule = Rule(self.domain, self.target, .67)

        self.assertEqual(rule.domains, {self.domain})
        self.assertEqual(rule.targets, {self.target})

        rule.domains.add(self.b)
        rule.targets.add(self.y)

        self.assertEqual(rule.domains, {self.domain, self.b, self.c})
        self.assertEqual(rule.targets, {self.target, self.x, self.y})

    def test_addWhileConditional(self):

        rule = Rule(self.domain, self.target, .67)
        rule.conditions.add(Condition("@", .08))

        self.assertEqual(rule.domains, {self.domain})
        self.assertEqual(rule.targets, {self.target})

        rule.domains.add(self.b)
        rule.targets.add(self.y)

        self.assertEqual(rule.domains, {self.domain, self.b, self.c})
        self.assertEqual(rule.targets, {self.target, self.x, self.y, self.z})

    def test_discard(self):

        rule = Rule({self.domain, self.b}, {self.target, self.y}, .89)

        self.assertEqual(rule.domains, {self.domain, self.b, self.c})
        self.assertEqual(rule.targets, {self.target, self.x, self.y})

        rule.domains.discard(self.b)
        rule.targets.discard(self.y)

        self.assertEqual(rule.domains, {self.domain})
        self.assertEqual(rule.targets, {self.target})

    def test_discardWhileConditional(self):

        rule = Rule({self.domain, self.b}, {self.target, self.y}, .89)
        rule.conditions.add(Condition("@", .08))

        self.assertEqual(rule.domains, {self.domain, self.b, self.c})
        self.assertEqual(rule.targets, {self.target, self.x, self.y, self.z})

        rule.domains.discard(self.b)
        rule.targets.discard(self.y)

        self.assertEqual(rule.domains, {self.domain})
        self.assertEqual(rule.targets, {self.target})

class Test_ConditionManager(unittest.TestCase):

    def setUp(self):

        self.a = Concept("A")
        self.b = Concept("B", parents={self.a})
        self.c = Concept("C", parents={self.b})

        self.x = Concept("X")
        self.y = Concept("Y", parents={self.x})
        self.z = Concept("Z", parents={self.y})

        self.relation = Relation({self.a}, "example", {self.x})

        self.rule = Rule(self.b, self.y, .67)

        self.relation.rules.add(self.rule)

    def test_add(self):
        # Test that adding a condition (and the other forms of add) add in the order of salience

        con1 = Condition("%", .78)
        con2 = Condition("%", .50)
        con3 = Condition("%", .62)

        self.assertEqual(list(self.rule.conditions), [])

        self.rule.conditions.add(con1)

        self.assertEqual(list(self.rule.conditions), [con1])

        self.rule.conditions.add(con2)
        self.rule.conditions.add(con3)

        self.assertEqual(list(self.rule.conditions), [con1, con3, con2])

    def test_addingTargetDependentCondition(self):
        # Test that adding the target dependent condition that it causes the targets to cascade

        # Target dependant condition
        con1 = Condition("@", .68)

        self.assertEqual(self.rule.targets, {self.y, self.x})

        self.rule.conditions.add(con1)

        self.assertEqual(self.rule.targets, {self.x, self.y, self.z})

    def test_cannotAddConditionTwice(self):
        # Assert that a condition cannot be added twice

        condition = Condition("@")

        self.rule.conditions.add(condition)

        with pytest.raises(ValueError):
            self.rule.conditions.add(condition)

        self.assertEqual(len(self.rule.conditions), 1)

    def test_remove(self):

        con1 = Condition("%", .78)
        con2 = Condition("%", .50)
        con3 = Condition("%", .62)

        self.rule.conditions.add(con1)
        self.rule.conditions.add(con2)
        self.rule.conditions.add(con3)

        self.rule.conditions.remove(con2)
        del self.rule.conditions[1]

        self.assertEqual(list(self.rule.conditions), [con1])

    def test_removeLastTargetDependentCondition(self):

        con1 = Condition("@", .68)
        con2 = Condition("@", .54)

        self.rule.conditions.add(con1)

        self.assertEqual(self.rule.targets, {self.x, self.y, self.z})

        self.rule.conditions.add(con2)
        self.rule.conditions.remove(con1)

        self.assertEqual(self.rule.targets, {self.x, self.y, self.z})

        self.rule.conditions.remove(con2)

        self.assertEqual(self.rule.targets, {self.x, self.y})


class Test_RulesWithPartials(unittest.TestCase):

    def setUp(self):

        self.a = Concept("A")
        self.b = Concept("B", parents={self.a})
        self.c = Concept("C", parents={self.b})

        self.x = Concept("X")
        self.y = Concept("Y", parents={self.x})
        self.z = Concept("Z", parents={self.y})


    def test_expandingConceptSet(self):

        rule = Rule(self.b, {self.y, "partial"}, .7)
        rule.conditions.add(Condition("@", .2))

        self.assertEqual(rule.targets, {self.x, self.y, self.z, "partial"})

if __name__ == "__main__":
    unittest.main()