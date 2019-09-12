import unittest
from itertools import product

from infogain.knowledge import Concept, Relation, Rule

class test_RelationInterface(unittest.TestCase):

    def setUp(self):

        self.a = Concept("A")
        self.b = Concept("B", parents={self.a})
        self.c = Concept("C", parents={self.b})

        self.d = Concept("D")
        self.e = Concept("E", parents={self.d})
        self.f = Concept("F", parents={self.e})

        self.x = Concept("X")
        self.y = Concept("Y", parents={self.x})
        self.z = Concept("Z", parents={self.y})

        self.singleRelation = Relation({self.a}, "example", {self.x})
        self.groupRelation = Relation([{self.a}, {self.d}], "example", [{self.d}, {self.x}])

    def test_domains(self):

        # Test that the call method on the domains returns all the concepts that appear within the domains of the rel
        self.assertEqual(self.singleRelation.domains(), {self.a, self.b, self.c})
        self.assertEqual(self.groupRelation.domains(), {self.a, self.b, self.c, self.d, self.e, self.f})

        # Test that iterating over the domains returns groups of domain concepts
        for i, domains in enumerate(self.singleRelation.domains):
            self.assertEqual(i, 0)
            self.assertEqual(domains, {self.a, self.b, self.c})

        for i, domains in enumerate(self.groupRelation.domains):
            self.assertTrue(i < 2)

            if i == 0:
                self.assertEqual(domains, {self.a, self.b, self.c})
            else:
                self.assertEqual(domains, {self.d, self.e, self.f})

        example1 = Concept("Example1")
        example2 = Concept("Example2")

        # Test the add feature of the domains
        self.singleRelation.domains.add(example1)

        self.assertTrue(example1 in self.singleRelation.domains())

        # Test the add to group of domains
        self.groupRelation.domains.add(example1)
        self.groupRelation.domains.add(example2, 1)

        for i, domains in enumerate(self.groupRelation.domains):

            self.assertIn(example1, domains)

            if i == 0:
                self.assertNotIn(example2, domains)
            else:
                self.assertIn(example2, domains)

    def test_targets(self):

        # Test that the call method on the domains returns all the concepts that appear within the domains of the rel
        self.assertEqual(self.singleRelation.targets(), {self.x, self.y, self.z})
        self.assertEqual(self.groupRelation.targets(), {self.d, self.e, self.f, self.x, self.y, self.z})

        # Test that iterating over the domains returns groups of domain concepts
        for i, targets in enumerate(self.singleRelation.targets):
            self.assertEqual(i, 0)
            self.assertEqual(targets, {self.x, self.y, self.z})

        for i, target in enumerate(self.groupRelation.targets):
            self.assertTrue(i < 2)

            if i == 0:
                self.assertEqual(target, {self.d, self.e, self.f})
            else:
                self.assertEqual(target, {self.x, self.y, self.z})

        example1 = Concept("Example1")
        example2 = Concept("Example2")

        # Test the add feature of the domains
        self.singleRelation.targets.add(example1)

        self.assertTrue(example1 in self.singleRelation.targets())

        # Test the add to group of domains
        self.groupRelation.targets.add(example1)
        self.groupRelation.targets.add(example2, 1)

        for i, target in enumerate(self.groupRelation.targets):

            self.assertIn(example1, target)

            if i == 0:
                self.assertNotIn(example2, target)
            else:
                self.assertIn(example2, target)

    def test_rules(self):

        rule1 = Rule(self.a, self.x, .95)
        rule2 = Rule(self.a, self.x, .85)
        rule3 = Rule(self.b, self.y, .70)

        self.singleRelation.rules.add(rule2)
        self.singleRelation.rules.add(rule3)
        self.singleRelation.rules.add(rule1)

        self.assertEqual(len(self.singleRelation.rules), 3)
        self.assertEqual(set(self.singleRelation.rules), {rule1, rule2, rule3})

        for rule, confidence in zip(self.singleRelation.rules, [.95, .85, .70]):
            self.assertEqual(rule.confidence, confidence)

    def test_between(self):

        # Basic between method
        self.assertTrue(self.singleRelation.between(self.b, self.x))
        self.assertFalse(self.singleRelation.between(self.y, self.b))

        # Group between
        self.assertTrue(self.groupRelation.between(self.a, self.d))
        self.assertFalse(self.groupRelation.between(self.a, self.x))
        self.assertTrue(self.groupRelation.between(self.d, self.x))
        self.assertFalse(self.groupRelation.between(self.d, self.a))

    def test_clone(self):

        cloned = self.singleRelation.clone()

        self.assertEqual(cloned.name, "example")
        self.assertEqual(cloned.domains(), {"A"})
        self.assertEqual(cloned.targets(), {"X"})

        cloned = self.groupRelation.clone()

        self.assertEqual(len(cloned.domains), 2)

class Test_Relation(unittest.TestCase):

    def test_initialisation_expansion_set_to_set(self):

        con1 = Concept("1")
        con2 = Concept("2", children={con1})
        con3 = Concept("3", children={con2})

        relation = Relation({con3},"relates",{con2})

        self.assertTrue(con1 in relation.targets)

        self.assertEqual(relation.domains(), {con1,con2,con3})
        self.assertEqual(relation.targets(), {con1,con2})

    def test_initialisation_expansion_group_to_group(self):

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})


        rel = Relation([[x1], [x2]], "rel", [[y1], [y2]])

        self.assertEqual(rel.domains(), {x1,x2,x11,x12})
        self.assertEqual({x.name for x in rel.targets()}, {x.name for x in {y1, y11, y2}})

        for dom in {x1, x11, x12}:
            [self.assertTrue(rel.between(dom, tar)) for tar in {y1, y11}]

        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))


    def test_initialisation_expansion_permeable(self):

        con1 = Concept("1", category=Concept.ABSTRACT)
        con2 = Concept("2", children={con1})
        con3 = Concept("3", children={con2})

        relation = Relation({con3},"relates",{con2})

        self.assertEqual(relation.domains(), {con1, con2,con3})
        self.assertEqual(relation.targets(), {con1, con2})

    def test_between(self):

        con1 = Concept("1")
        con2 = Concept("2", children={con1})

        conA = Concept("A")
        conB = Concept("B", children={conA})

        relation = Relation({con2}, "relates", {conB})

        self.assertTrue(relation.between(con2, conB))
        self.assertTrue(relation.between(con1, conA))

    def test_between_differ(self):

        con1, con2, con3 = Concept("1"), Concept("2"), Concept("3")

        none_differ_relation = Relation({con1, con2}, "A", {con1, con2})
        differ_relation = Relation({con1, con2}, "B", {con1, con2}, differ=True)

        for a, b in product([con1, con2], [con1, con2]):

            self.assertTrue(none_differ_relation.between(a, b))
            self.assertFalse(none_differ_relation.between(a, con3))

            if a is b: self.assertFalse(differ_relation.between(a,b))
            else: self.assertTrue(differ_relation.between(a,b))


    def test_RelationUpdateRuleOnConceptUpdate(self):
        """ Assert that when a concept inherits the relation, that it is correctly linked with its rules """

        a, b = Concept("A"), Concept("B")
        a1, b1, = Concept("A1", parents={a}), Concept("B1", parents={b})

        rel = Relation({a}, "test", {b1})
        rule = Rule(a,  b1)
        rel.rules.add(rule)

        self.assertEqual(rule.domains, {a, a1})

        a11 = Concept("A11", parents={a1})

        self.assertEqual(rule.domains, {a, a1, a11})

    def test_RelationAppendConceptSet(self):

        # Define the concept and relation
        con1, con2, con3 = Concept("1"), Concept("2"), Concept("3")
        rel = Relation({con1, con2}, "A", {con1, con2})

        # Add another ConceptSet Paring
        rel.appendConceptSets({con3}, {con3})

        # Test that the sets are correctly added
        one, two = zip(rel.domains, rel.targets)
        self.assertEqual(one, ({con1, con2}, {con1, con2}))
        self.assertEqual(two, ({con3}, {con3}))

if __name__ == "__main__":
    unittest.main()