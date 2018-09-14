import unittest, mock, sys

from infogain.artefact import Document, Datapoint, score, annotate
from infogain.extraction import RelationExtractor
from infogain.resources.ontologies import language

class Test_Document_Functions(unittest.TestCase):

    def test_score_function(self):

        # TODO: TO FINISH CORRECT THIS
        # shouldn't use the actual relation extractor to run
        # To much cross package dependances going on here

        return

        training, test = language.training()[:-1], language.training()[-1]

        # Train
        extractor = RelationExtractor(ontology=language.ontology(), min_count=1)
        extractor.fit(training)

        test = extractor.predict(test)

        corpus, _ = score(extractor, test)

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
            document = annotate(language.ontology(), document)

        self.assertEqual(len(document), 3)
        for point in document.datapoints():
            self.assertTrue(point.annotation, 0)
        
