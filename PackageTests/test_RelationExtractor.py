import os, unittest
from . import LANGUAGE_ONTOLOGY

from InfoGain import RelationExtractor, Ontology

class Test_RelationExtractor(unittest.TestCase):

    def setUp(self):
        with open(LANGUAGE_ONTOLOGY) as f:
            print(f.read())
        print(LANGUAGE_ONTOLOGY)
        self.ontology = Ontology(filepath=LANGUAGE_ONTOLOGY)

    def test_ExtractorGeneration(self):
        """ Extractor object """
        extractor = RelationExtractor(ontology=self.ontology, k=20)