import unittest

from infogain.artefact import Datapoint
from infogain.extraction import Embedder, RelationModel
from infogain.resources.ontologies import language

class Test_Relation_Model(unittest.TestCase):

    def test_RelationFittingAndPredicting(self):  # TODO: Break this down into different tests.
        # Create the model
        relationModel = RelationModel("speaks")

        # Collect training documents
        fitDocument = language.training(1)[0]
        
        # Create a model to embed the datapoints
        embedder = Embedder()
        embedder.train(fitDocument.sentences())

        # Collect and embedd the training datapoints
        fitData = fitDocument.datapoints()
        [point.embedContext(embedder.sentence) for point in fitData]

        relationModel.fit(fitData)

        # Collect some testing datapoints for the model
        predictData = language.testing(1)[0].datapoints()
        [point.embedContext(embedder.sentence) for point in predictData]

        relationModel.predict(predictData)



