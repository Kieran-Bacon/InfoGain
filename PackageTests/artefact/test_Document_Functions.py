import unittest, sys
from unittest import mock

from infogain.artefact import Document, Annotation, score, annotate
from infogain.resources.ontologies import language

class Test_Document_Functions(unittest.TestCase):

    def setUp(self):
        self.ont_language = language.ontology()

    def test_score_function(self):

        # Collect a training document
        training = Document(content = "Luke can speak English. Kieran can speak English. Kieran cannot speak French")
        training.processKnowledge(self.ont_language)

        # Assign an annotation, and prediction to each of the datapoints like the RelationExtractor would
        for datapoint, ann in zip(training.datapoints(), [1, 1, 0]):
            datapoint.annotation = ann
            datapoint.prediction = 1

        # Run the function on the document
        corpus, _ = score(self.ont_language, [training])

        self.assertEqual(2/3, corpus["precision"])
        self.assertEqual(1, corpus["recall"])
        self.assertAlmostEqual(0.8, corpus["f1"])

    def test_annotate_function(self):
        """ Test the annotation function """

        document = Document(content="Luke can speak English rather well, but Luke doesn't live in England.")

        with mock.patch('builtins.input', side_effect=["N"] + ["0"]*7):
            annotate(self.ont_language, document)

        self.assertTrue(len(document) == 7)
        for point in document.datapoints():
            self.assertTrue(point.annotation == 0)