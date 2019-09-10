import os
import unittest
import pytest
import tempfile

from infogain.artefact import Document, Entity, Annotation
from infogain import Serialiser

class Test_JsonDocumentSerialising(unittest.TestCase):

    def test_saveLoadSimpleDocument(self):
        document = Document("This is a document stating that Kieran can speak English")
        kieran, english = Entity("Person", "Kieran"), Entity("Language", "English")

        document.entities.add(kieran, 32)
        document.entities.add(english, 49)
        document.annotations.add(Annotation(kieran, "speaks", english, classification=Annotation.POSITIVE))

        with tempfile.TemporaryDirectory() as directory:
            filepath = os.path.join(directory, 'temp.dig')

            json = Serialiser("json", Document)
            json.save(document, filepath)
            rebuilt = json.load(filepath)

            self.assertEqual(document.content, rebuilt.content)

            for e1, e2 in zip(document.entities, rebuilt.entities):
                self.assertEqual(e1.classType, e2.classType)
                self.assertEqual(e1.surfaceForm, e2.surfaceForm)

            for ann1, ann2 in zip(document.annotations, rebuilt.annotations):
                self.assertEqual(ann1.domain.surfaceForm, ann2.domain.surfaceForm)
                self.assertEqual(ann1.name, ann2.name)
                self.assertEqual(ann1.target.surfaceForm, ann2.target.surfaceForm)

    def test_saveLoadSplitDocument(self):
        document = Document(
            "This is a document stating that Kieran can speak English."
            "This content is going to be split better."
        )
        kieran, english, better = Entity("Person", "Kieran"), Entity("Language", "English"), Entity("Package", 'better')

        document.entities.add(kieran, 32)
        document.entities.add(english, 49)
        document.entities.add(better, 57 + 34)
        document.annotations.add(Annotation(kieran, "speaks", english, classification=Annotation.POSITIVE))

        document.split(r"\.")

        with tempfile.TemporaryDirectory() as directory:
            filepath = os.path.join(directory, 'temp.dig')

            json = Serialiser("json", Document)
            json.save(document, filepath)
            rebuilt = json.load(filepath)

            self.assertEqual(document.content, rebuilt.content)

            for e1, e2 in zip(document.entities, rebuilt.entities):
                self.assertEqual(e1.classType, e2.classType)
                self.assertEqual(e1.surfaceForm, e2.surfaceForm)

            for ann1, ann2 in zip(document.annotations, rebuilt.annotations):
                self.assertEqual(ann1.domain.surfaceForm, ann2.domain.surfaceForm)
                self.assertEqual(ann1.name, ann2.name)
                self.assertEqual(ann1.target.surfaceForm, ann2.target.surfaceForm)
