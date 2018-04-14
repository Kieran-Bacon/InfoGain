import os, unittest
from . import DOCUMENTS, ONTOLOGIES

from InfoGain import Ontology, PredictionDocument

class Test_PredictionDocument(unittest.TestCase):
    """ Test the functionality and inner workings of the generic prediction document """

    def test_content_load(self):
        """ Generate a document with content that has been passed to the document """
        contents = "When I generate a document in this manner, I want to ensure that the document "+\
        "object is created correctly. This is the initial test! Fingers crossed!!! Testing sentence end."

        cleanedContents = "when i generate a document in this manner i want to ensure that the " +\
        "document object is created correctly this is the initial test fingers crossed testing sentence end"

        document = PredictionDocument(content=contents)

        # Check that only a single paragraph has been loaded.
        self.assertEqual(len(document.paragraphs), 1)
        self.assertEqual(len(document.cleanedParagraphs), 1)

        # Check that correct number of sentences is generated
        self.assertEqual(len(document.paragraphs[0]), 2)
        self.assertEqual(len(document.cleanedParagraphs[0]),2)

        # Check the contents are complete
        self.assertEqual(document.text(), contents)
        self.assertEqual(document.cleanText(), cleanedContents)

    def test_document_processKnowledge(self):
        ont = Ontology(filepath=os.path.join(ONTOLOGIES, "languages.json"))
        doc = PredictionDocument(filepath=os.path.join(DOCUMENTS, "Predictlanguages.txt"))

        doc.processKnowledge(ont)