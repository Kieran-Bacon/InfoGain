import os, unittest
from . import DOCUMENTS, ONTOLOGIES

from InfoGain import Ontology, Document, TrainingDocument

class Test_Document(unittest.TestCase):

    def setUp(self):
        pass

    def test_document_init(self):
        # TODO: Place holder for verifying paragraphs and sentences
        pass

    def test_document_processKnowledge(self):
        ont = Ontology(filepath=os.path.join(ONTOLOGIES, "languages.json"))
        doc = Document(filepath=os.path.join(DOCUMENTS, "Predictlanguages.txt"))

        doc.processKnowledge(ont)

    def test_document_text(self):
        raise NotImplementedError()

    def test_TrainingDocument_Load(self):
        """Open a valid training document structure and verify that its attributes are correct"""
        document = TrainingDocument(filepath=os.path.join(DOCUMENTS, "training.json"))

        self.assertEqual(len(document), 210)

if __name__ == "__main__":
    unittest.main()