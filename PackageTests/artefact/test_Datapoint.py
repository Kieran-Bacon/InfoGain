import os, unittest, pytest

from infogain.artefact import Datapoint, IncompleteDatapoint
from infogain.extraction import Embedder
from infogain.exceptions import ConsistencyError

class Test_Datapoint(unittest.TestCase):

    def setUp(self):
        self.embeddingModel = Embedder()

    def test_attribute_assignment(self):
        """ Test that the assignment of attributes to the datapoint are correctly validated

        There are three properties that are protected:
         - annotation
         - prediction
         - probability
        """

        point = Datapoint()
        incorrect_values = [1.1, -0.9, "Well this is just simply not a value..."]

        for incorrect_value in incorrect_values :
            with pytest.raises(ConsistencyError): point.prediction = incorrect_value
            with pytest.raises(ConsistencyError): point.probability = incorrect_value
            with pytest.raises(ConsistencyError): point.annotation = incorrect_value

        point.prediction = 1
        point.annotation = 0
        point.probability = 0.5

        self.assertTrue(point.prediction is point.POSITIVE)
        self.assertTrue(point.annotation is point.INSUFFICIENT)
        self.assertTrue(point.probability == 0.5)

    def test_embedding_context(self):

        # Check that the datapoint will correctly indicate if the context has not been set
        with pytest.raises(IncompleteDatapoint):
            Datapoint().embedContext(self.embeddingModel.sentence)

        # Build a datapoint with context and embed it, check that the values are correctly embedded
        context_point = Datapoint({"context":{"left":"Some text", "middle": "Some text", "right": "other text"}})
        context_point.embedContext(self.embeddingModel.sentence)

        self.assertEqual(len(context_point.embedding["left"]), self.embeddingModel.size())
        self.assertEqual(list(context_point.embedding["left"]), list(context_point.embedding["middle"]))
        self.assertNotEqual(list(context_point.embedding["left"]), list(context_point.embedding["right"]))

    def test_features(self):

        # Check something with no embeddings
        with pytest.raises(IncompleteDatapoint):
            Datapoint().features()

        # Build a datapoint with context and embed it, check that the values are correctly embedded
        point = Datapoint({"context":{"left":"Some text", "middle": "Some text", "right": "other text"}})
        point.embedContext(self.embeddingModel.sentence)

        self.assertEqual(
            point.features(),
            (
                [point.embedding["left"],
                point.embedding["middle"],
                point.embedding["right"]],
                point.annotation
            )
        )

    def test_minimise(self):

        data = {
                    "domain": {"concept": "x", "text": "a"},
                    "target": {"concept": "x", "text": "b"},
                    "relation": "y",
                    "text": "sentence",
                    "context": {
                        "left": "sentence[:p1[0]].strip()",
                        "middle": "sentence[p1[1]:p2[0]].strip()",
                        "right": "sentence[p2[1]:].strip()"
                    },
                    "prediction": None,
                    "probability": None,
                    "annotation": None
                }

        self.assertEqual(data, Datapoint(data).minimise())




