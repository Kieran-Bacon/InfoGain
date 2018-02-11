import os, unittest
from . import LOCATION

from InfoGain import Ontology, TrainingDocument

class Test_Document(unittest.TestCase):

    def setUp(self):
        self.medicalOntologyLocation = os.path.join(LOCATION, "Resources/Ontologies/medical.ont")
        self.trainingDocumentLocation = os.path.join(LOCATION, "Resources/Documents/training.json")
        pass

    def test_document_text(self):
        pass

    def test_TrainingDocument_Load(self):
        """Open a valid training document structure and verify that its attributes are correct"""
        documentOntology = Ontology("Medical", filepath=self.medicalOntologyLocation)
        document = TrainingDocument(documentOntology, filepath=self.trainingDocumentLocation)

        self.assertEqual(len(document.datapoints), 210)
        self.assertEqual(len(documentOntology.concept("Drug").textRepr()),162)
        self.assertEqual(len(documentOntology.concept("Dose").textRepr()),127)

if __name__ == "__main__":
    unittest.main()