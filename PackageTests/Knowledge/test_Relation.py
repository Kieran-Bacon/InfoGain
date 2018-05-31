import unittest

from InfoGain.Knowledge import Concept, Relation

class Test_Relation(unittest.TestCase):

    def test_initialisation_expansion(self):

        con1 = Concept("1")
        con2 = Concept("2", children={con1})
        con3 = Concept("3", children={con2})

        relation = Relation({con3},"relates",{con2})

        self.assertTrue(con1 in relation.targets)

        self.assertEqual(relation.domains, {con1,con2,con3})
        self.assertEqual(relation.targets, {con1,con2})

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
        con1.children.add(con3)

        self.assertTrue(con2 == "2")

        relation = Relation({con1}, "speaks", {con2})

        mini = relation.minimise()

        self.assertEqual(mini["name"], "speaks")
        self.assertEqual(set(mini["domains"]), {con2.name})
        self.assertEqual(set(mini["targets"]), {con2.name})

if __name__ == "__main__":
    unittest.main()