import os, unittest
from . import LOCATION

from InfoGain import Ontology, TrainingDocument

class Test_Document(unittest.TestCase):

    def setUp(self):
        self.trainingDocumentLocation = os.path.join(LOCATION, "Resources/Documents/training.json")

    def test_document_text(self):
        raise NotImplementedError()

    def test_TrainingDocument_Load(self):
        """Open a valid training document structure and verify that its attributes are correct"""
        document = TrainingDocument(filepath=self.trainingDocumentLocation)

        self.assertEqual(len(document), 210)

if __name__ == "__main__":
    unittest.main()