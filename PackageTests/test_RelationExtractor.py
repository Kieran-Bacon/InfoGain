import os, unittest
from . import DOCUMENTS, ONTOLOGIES, PATHS

from InfoGain import Ontology, Document, TrainingDocument, RelationExtractor

class Test_RelationExtractor(unittest.TestCase):

    def setUp(self):

        self.paths = {
            "language":{
                "ontology": os.path.join(ONTOLOGIES, "languages.json"),
                "training": [os.path.join(DOCUMENTS,"language","training","tr1.json")],
                "predicting": [os.path.join(DOCUMENTS,"language","prediction","pr1.txt")]
            },
            "medicine":{
                "ontology": os.path.join(ONTOLOGIES, "medical.json"),
                "training": [os.path.join(DOCUMENTS, "medicine", "training",  "tr1.json")],
                "predicting": [os.path.join(DOCUMENTS, "medicine", "prediction", "pr1.txt")]
            }
        }

    def test_loadExtractor_from_file(self):
        extractor = RelationExtractor(filepath=self.paths["medicine"]["ontology"])

        self.assertEqual(len(extractor._concepts), 3)
        self.assertEqual(len(extractor._relations), 2)

    def test_ExtractorGeneration(self):
        """ Extractor object """

        # Load Training documents
        training = [TrainingDocument(filepath=x) for x in self.paths["language"]["training"]]
        predicting = [Document(filepath=x) for x in self.paths["language"]["predicting"]]

        extractor = RelationExtractor(filepath=PATHS["language"]["ontology"])
        extractor.fit(training)
        extractor.predict(predicting)

        for doc in predicting:
            for points in doc.datapoints():
                print("point:", points.text)
                #self.assertEqual(points.prediction, "NO")