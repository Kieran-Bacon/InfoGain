import unittest

from InfoGain import Concept

class Test_Concept(unittest.TestCase):

    def setUp(self):
        # Set up of concepts
        self.concept = Concept("Kieran",False)
        self.parentConcept = Concept("Student",False)
        self.grandparentConcept = Concept("Person", False)

        # Assigining concept
        self.parentConcept.addParent(self.grandparentConcept)
        self.grandparentConcept.addChild(self.parentConcept)

    def test_init_function(self):
        """ Test that the expected values of the concept object are correct """
        self.assertEqual(self.concept.name, "Kieran")
        self.assertFalse(self.concept.permeable)
        self.assertEqual(self.concept.children, set())
        self.assertEqual(self.concept.parents, set())

    def test_addChild(self):
        """ Assert add child correctly alters object contents """

        self.assertEqual(self.parentConcept.children, set())
        self.parentConcept.addChild(self.concept)
        self.assertEqual(self.parentConcept.children, {self.concept})

    def test_removeChild(self):

        self.assertEqual(self.grandparentConcept.children, {self.parentConcept})
        self.grandparentConcept.removeChild(self.parentConcept)
        self.assertEqual(self.grandparentConcept.children, set())

    def test_addParent(self):
        """ Assert that the set is manipulated as expected and contains 
        the expected concept. """

        self.assertEqual(self.concept.parents, set())
        self.concept.addParent(self.parentConcept)
        self.assertEqual(self.concept.parents, {self.parentConcept})

    def test_removeParent(self):

        self.assertEqual(self.parentConcept.parents, {self.grandparentConcept})
        self.parentConcept.removeParent(self.grandparentConcept)
        self.assertEqual(self.parentConcept.parents, set())

    def test_isChildOf(self):
        self.assertEqual(self.parentConcept.parents, {self.grandparentConcept})
        self.assertTrue(self.parentConcept.isChildOf(self.grandparentConcept))

    def test_isParentOf(self):
        """ Test whether parents work as expected """
        self.assertEqual(self.grandparentConcept.children, {self.parentConcept})
        self.assertTrue(self.grandparentConcept.isParentOf(self.parentConcept))
        
    def test_isDescendantOf(self):
        self.concept.addParent(self.parentConcept)
        self.assertTrue(self.concept.isDecendantOf(self.grandparentConcept))

    def test_isAncestorOf(self):
        self.parentConcept.addChild(self.concept)
        self.assertTrue(self.grandparentConcept.isAncestorOf(self.concept))

    def test_ancestors(self):
        self.concept.addParent(self.parentConcept)
        self.assertEqual(self.concept.ancestors(), {self.parentConcept, self.grandparentConcept})

    def test_descendants(self):
        self.parentConcept.addChild(self.concept)
        self.assertEqual(self.grandparentConcept.descendants(), {self.concept, self.parentConcept})

if __name__ == "__main__":
    unittest.main()