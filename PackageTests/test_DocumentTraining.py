import os, unittest, json
from . import DOCUMENTS, PATHS

from InfoGain import TrainingDocument

class Test_TrainingDocument(unittest.TestCase):
    
    def test_TrainingDocument_Load(self):
        """Open a valid training document structure and verify that its attributes are correct"""
        
        document = TrainingDocument(filepath=PATHS["medicine"]["training"][0])

        # Open the document and count the number of datapoints present
        with open(PATHS["medicine"]["training"][0]) as testHandler:
            contents = json.load(testHandler)

        # Assert that at least that many datapoints are within the document
        self.assertEqual(len(document), len(contents["datapoints"]))

    def test_conceptMapping_after_generation(self):
        """ When the training document is made, a map between the instance names and the concepts 
        must be formed, ensure that it correctly does this """

        document = TrainingDocument(filepath=PATHS["medicine"]["training"][0])
        pass