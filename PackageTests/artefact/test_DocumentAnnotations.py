import unittest
import pytest

from infogain.artefact import Entity, Annotation
from infogain.artefact.document2 import Document

class Test_DocumentAnnotations(unittest.TestCase):

    def setUp(self):

        self.document = Document(
            "A block of text talking about how, Kieran speaks English."
            " He's been speaking it for a while. Kieran can speak lots of languages. Such as French"
        )

        self.e0 = Entity('Action', 'talking')
        self.e1 = Entity('Person', 'Kieran')
        self.e2 = Entity('Language', 'English')
        self.e3 = Entity('Person', 'Kieran')
        self.e4 = Entity('Language', 'French')

        for e, i in [(self.e0, 16), (self.e1, 35), (self.e2, 49), (self.e3, 57 + 36), (self.e4,57 + 80)]:
            self.document.entities.add(e, i)


        self.a0 = Annotation(self.e0, "enactedBy", self.e1)
        self.a1 = Annotation(self.e1, "speaks", self.e2)
        self.a2 = Annotation(self.e3, "speaks", self.e4)

    def test_add(self):

        self.document.annotations.add(self.a0)
        self.document.annotations.add(self.a1)

        with pytest.raises(NotImplementedError):
            self.document.annotations.add(self.a2)

        self.assertEqual(len(self.document.annotations), 2)
        self.assertEqual(set(self.document.annotations), {self.a0, self.a1})


    def test_split(self):

        self.document.annotations.add(self.a0)
        self.document.annotations.add(self.a1)

        self.document.split(',')

        self.assertEqual(len(self.document.annotations), 1)
        self.assertEqual(set(self.document.annotations), {self.a1})

    def test_join(self):

        self.document.annotations.add(self.a0)
        self.document.annotations.add(self.a1)

        self.document.split(',')
        self.document.join("something")

        self.assertEqual(len(self.document.annotations), 1)
        self.assertEqual(set(self.document.annotations), {self.a1})

    def test_removeEntities(self):

        self.document.annotations.add(self.a0)
        self.document.annotations.add(self.a1)

        self.assertEqual(len(self.document.annotations), 2)
        self.assertEqual(set(self.document.annotations), {self.a0, self.a1})

        self.document.annotations.remove(self.a0)

        self.assertEqual(len(self.document.annotations), 1)
        self.assertEqual(set(self.document.annotations), {self.a1})

