import os, unittest, json
from . import DOCUMENTS

from InfoGain import TrainingDocument

class Test_TrainingDocument(unittest.TestCase):

    def setUp(self):
        self.training_location = os.path.join(DOCUMENTS, "training.json")
    
    def test_TrainingDocument_Load(self):
        """Open a valid training document structure and verify that its attributes are correct"""
        
        document = TrainingDocument(filepath=self.training_location)

        # Open the document and count the number of datapoints present
        with open(self.training_location) as testHandler:
            contents = json.load(testHandler)

        # Assert that at least that many datapoints are within the document
        self.assertEqual(len(document), len(contents["datapoints"]))

    def test_conceptMapping_after_generation(self):
        """ When the training document is made, a map between the instance names and the concepts 
        must be formed, ensure that it correctly does this """

        document = TrainingDocument(filepath=self.training_location)

        self.assertEqual(document._concepts, {})

        