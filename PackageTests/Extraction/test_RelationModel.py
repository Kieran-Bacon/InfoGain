import unittest

from InfoGain.Documents import Datapoint
from InfoGain.Extraction import RelationModel
from InfoGain.Resources import Language, Models

class Test_Relation_Model(unittest.TestCase):

    def test_RelationFittingAndPredicting(self):
        # Create the model
        relationModel = RelationModel("speaks")

        # Collect training documents
        fitDocument = Language.training(1)[0]
        
        # Create a model to embed the datapoints
        embedder = Models.Embedder()
        embedder.train(fitDocument.sentences())

        # Collect and embedd the training datapoints
        fitData = fitDocument.datapoints()
        [point.embedContext(embedder.sentence) for point in fitData]

        relationModel.fit(fitData)

        # Collect some testing datapoints for the model
        predictData = Language.testing(1)[0].datapoints()
        [point.embedContext(embedder.sentence) for point in predictData]

        relationModel.predict(predictData)



