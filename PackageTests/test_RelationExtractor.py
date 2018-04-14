import os, unittest
from . import DOCUMENTS, ONTOLOGIES

from InfoGain import Ontology, PredictionDocument, TrainingDocument, RelationExtractor

class Test_RelationExtractor(unittest.TestCase):

    def setUp(self):
        self.training = TrainingDocument(filepath=os.path.join(DOCUMENTS, "training.json"))
        #self.testing = PredictionDocument(filepath=os.path.join(DOCUMENTS, "testing.txt"))
        self.ontology = Ontology(filepath=os.path.join(ONTOLOGIES, "medical.ont"))

    def test_ExtractorGeneration(self):
        """ Extractor object """
        extractor = RelationExtractor(ontology=self.ontology, k=20)
        extractor.fit(self.training)
        #extractor.predict(self.testing)
