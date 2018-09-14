import unittest
from itertools import product

from infogain.knowledge import Concept, Relation

class Test_Relation(unittest.TestCase):

    def test_initialisation_expansion_set_to_set(self):

        con1 = Concept("1")
        con2 = Concept("2", children={con1})
        con3 = Concept("3", children={con2})

        relation = Relation({con3},"relates",{con2})

        self.assertTrue(con1 in relation.targets)

        self.assertEqual(relation.domains, {con1,con2,con3})
        self.assertEqual(relation.targets, {con1,con2})

    def test_initialisation_expansion_group_to_group(self):

        x = Concept("x")
        x1, x2 = Concept("x1", {x}), Concept("x2", {x})
        x11, x12 = Concept("x11", {x1}), Concept("x12", {x1})

        y = Concept("y")
        y1, y2 = Concept("y1", {y}), Concept("y2", {y})
        y11 = Concept("y11", {y1})


        rel = Relation([[x1], [x2]], "rel", [[y1], [y2]])

        self.assertEqual(rel.domains, {x1,x2,x11,x12})
        self.assertEqual({x.name for x in rel.targets}, {x.name for x in {y1, y11, y2}})

        for dom in {x1, x11, x12}:
            [self.assertTrue(rel.between(dom, tar)) for tar in {y1, y11}]

        self.assertTrue(rel.between(x2, y2))
        self.assertFalse(rel.between(x2, y1))


    def test_initialisation_expansion_permeable(self):

        con1 = Concept("1")
        con1.permeable = True
        con2 = Concept("2", children={con1})
        con3 = Concept("3", children={con2})

        relation = Relation({con3},"relates",{con2})

        self.assertEqual(relation.domains, {con2,con3})
        self.assertEqual(relation.targets, {con2})

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

    def test_differ_minimise(self):

        con1, con2 = Concept("1"), Concept("2")

        differ_relation = Relation({con1, con2}, "A", {con1, con2}, differ=True)

        minimised = differ_relation.minimise()

        self.assertTrue(minimised["differ"])


    def test_subscribe(self):

        # Test that a subscribed concept is currectly added to the shindig
        con1, conA = Concept("1"), Concept("B")
        conB = Concept("B", parents={con1, conA})

        relation = Relation({con1}, "relates", {conA})

        relation.subscribe(conB)

        self.assertTrue(relation.between(conB, conB))

        # Test that a concept that doesn't share any ancestors is not added
        conC = Concept("C")

        relation.subscribe(conC)

        self.assertEqual(relation.domains,{con1, conB})
        self.assertEqual(relation.targets,{conA, conB})

    def test_permeable_subscribe(self):

        con1 = Concept("1")
        con2 = Concept("2", parents={con1})
        con2.permeable = True
        con3 = Concept("3", parents={con2})

        relation = Relation({con1},"relates",{con1})
        
        relation.subscribe(con2)
        relation.subscribe(con3)

        self.assertEqual(relation.domains, {con1, con3})
        self.assertEqual(relation.targets, {con1, con3})

    def test_minimise(self):

        con1 = Concept("1")
        con1.permeable = True
        con2 = Concept("2", parents={con1})
        con1.children.add(con2)
        con3 = Concept("3", parents={con2})
        con2.children.add(con3)

        self.assertTrue(con2 == "2")

        relation = Relation({con1}, "speaks", {con2})

        mini = relation.minimise()

        self.assertEqual(mini["name"], "speaks")

        self.assertEqual(set(mini["domains"][0]), {con2.name})
        self.assertEqual(set(mini["targets"][0]), {con2.name})

if __name__ == "__main__":
    unittest.main()