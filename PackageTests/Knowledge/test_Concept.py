import unittest

#from InfoGain import Concept

from InfoGain.Knowledge import Concept

class Test_Concept(unittest.TestCase):

    def test_initialisation_family_linking(self):

        person = Concept("Person", children={"Kieran", "Luke"})
        kieran = Concept("Kieran", parents={person})

        self.assertTrue(kieran in person.children)
        self.assertTrue(person in kieran.parents)
        self.assertTrue("Luke" in person.children)

    def test_ancestors_full_concepts(self):

        grandfather = Concept("Grand Father")
        father = Concept("Father", parents={grandfather})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {grandfather, father})

    def test_ancestores_partial_concepts(self):

        father = Concept("Father", parents={"Grand Father"})
        child = Concept("Child", parents={father})

        self.assertEqual(child.ancestors(), {father, "Grand Father"})

        child = Concept("Child", parents={"John"})

        self.assertEqual(child.ancestors(), {"John"})

    def test_descendants_full_concepts(self):

        grandson = Concept("Grand Son")
        son = Concept("Son", children={grandson})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, grandson})

    def test_descendants_partial_concepts(self):

        son = Concept("Son", children={"Grand Son"})
        person = Concept("Person", children={son})

        self.assertEqual(person.descendants(), {son, "Grand Son"})

        person = Concept("Person",children={"Son"})
        self.assertEqual(person.descendants(), {"Son"})

    def test_minimise(self):

        concept = Concept("Name")
        mini = concept.minimise()

        self.assertEqual(mini["name"], "Name")
        self.assertEqual(mini["parents"], [])
        self.assertEqual(mini["children"], [])
        self.assertFalse(mini["permeable"])
        self.assertEqual(mini["properties"], {})
        self.assertEqual(mini["alias"], [])

        concept = Concept("Name", parents={"Kieran"}, children={"What", "hey"})
        concept.alias.add("Badass")
        concept.properties["age"] = 24
        mini = concept.minimise()

        self.assertEqual(mini["name"], "Name")
        self.assertEqual(mini["parents"], ["Kieran"])
        self.assertEqual(set(mini["children"]), set(["What", "hey"]))
        self.assertFalse(mini["permeable"])
        self.assertEqual(mini["properties"], {"age": 24})
        self.assertEqual(mini["alias"], ["Badass"])

if __name__ == "__main__":
    unittest.main()