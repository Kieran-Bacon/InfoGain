import unittest
import pytest

from infogain.artefact import Entity, Annotation
from infogain.artefact.document2 import Document

class Test_Annotation(unittest.TestCase):

    def setUp(self):
        self.e1 = Entity("Person", "Kieran", 0.9)
        self.e2 = Entity("Language", "English", 1.)
        self.e3 = Entity("Object", "Ball")

    def test_init(self):

        ann = Annotation(self.e1, "speaks", self.e2, classification=Annotation.POSITIVE)

        self.assertEqual(ann.domain, self.e1)
        self.assertEqual(ann.annotationType, "speaks")
        self.assertEqual(ann.target, self.e2)
        self.assertEqual(ann.classification, Annotation.POSITIVE)
        self.assertEqual(ann.confidence, 1.)
        self.assertEqual(ann.annotation, None)

    def test_SetDomainTarget(self):

        ann = Annotation(self.e1, "speaks", self.e2)

        ann.domain = ann.target = self.e3

        self.assertEqual(ann.domain, self.e3)
        self.assertEqual(ann.target, self.e3)

        with pytest.raises(ValueError):
            ann.domain = 100

        with pytest.raises(ValueError):
            ann.target = 100

    def test_confidence(self):

        ann = Annotation(self.e1, "speaks", self.e2)

        ann.confidence = 0.4

        self.assertEqual(ann.confidence, .4)

        with pytest.raises(ValueError):
            ann.confidence = 100
        with pytest.raises(ValueError):
            ann.confidence = "something"

    def test_classifcation(self):

        ann = Annotation(self.e1, "speaks", self.e2)

        ann.classification = Annotation.NEGATIVE

        self.assertEqual(ann.classification, Annotation.NEGATIVE)

        with pytest.raises(TypeError):
            ann.classification = 100

    def test_annotation(self):

        ann = Annotation(self.e1, "speaks", self.e2, annotation=Annotation.NEGATIVE)
        self.assertEqual(ann.annotation, Annotation.NEGATIVE)
        with pytest.raises(TypeError):
            ann.annotation = 100


        ann = Annotation(self.e1, "speaks", self.e2)
        ann.annotation = Annotation.NEGATIVE
        self.assertEqual(ann.annotation, Annotation.NEGATIVE)
        with pytest.raises(TypeError):
            ann.annotation = 100

    def test_context(self):

        document = Document("Kieran can speak English really well.")

        # Add entities to the document
        document.entities.add(self.e1)
        document.entities.add(self.e2, 17)

        # Add annotation
        ann = Annotation(self.e1, "speaks", self.e2)

        self.assertIs(ann.context, None)

        document.annotations.add(ann)

        self.assertEqual(ann.context,
            (
                "",
                "can speak",
                "really well"
            )
        )

        with pytest.raises(ValueError):
            ann.context = ("something", "else", "")

    def test_embedding(self):

        document = Document("Kieran can speak English really well.")

        # Add entities to the document
        document.entities.add(self.e1)
        document.entities.add(self.e2, 17)

        # Add annotation
        ann = Annotation(self.e1, "speaks", self.e2)

        document.annotations.add(ann)

        ann.embedding = ([1,2,3],[2,1,3],[123,321,231])

        self.assertEqual(ann.embedding, ([1,2,3],[2,1,3],[123,321,231]))

        document.annotations.remove(ann)

        with pytest.raises(RuntimeError):
            ann.embedding = ([1,2,3],[2,1,3],[123,321,231])