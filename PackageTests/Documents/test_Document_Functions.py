import unittest, mock, sys

from InfoGain.Resources import Language

from InfoGain.Documents import Document, Datapoint, score, annotate
from InfoGain.Extraction import RelationExtractor


class Test_Document_Functions(unittest.TestCase):

    def test_score_function(self):

        ont = Language.ontology()
        training, test = Language.training()[:-1], Language.training()[-1]

        # Train
        extractor = RelationExtractor(ontology=Language.ontology(), min_count=1)
        extractor.fit(training)

        extractor.predict(test)

        corpus, _ = score(ont, test)

        self.assertTrue(0 < corpus["precision"])
        self.assertTrue(0 < corpus["recall"])
        self.assertTrue(0 < corpus["f1"])

    #@mock.patch("input")
    def test_annotate_function(self):
        """ Test the annotation function """

        document = Document(content="Luke can speak English rather well, but Luke doesn't live in England.")

        #TODO: Correctly mock the built in input function as to allow for the automation of this method
        ## Or wait till the annotation method is changed to something much much nicer and move
        return
        
        with mock.patch("builtins.input") as mock_input:
            mock_input.return_value = iter(["N", "0", "0", "0"])
            document = annotate(Language.ontology(), document)

        self.assertEqual(len(document), 3)
        for point in document.datapoints():
            self.assertTrue(point.annotation, 0)
        
