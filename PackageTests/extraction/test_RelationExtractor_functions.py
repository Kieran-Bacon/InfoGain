import os, unittest, pytest

from infogain.artefact import Document
from infogain.extraction import RelationExtractor, RelationModel
from infogain.extraction.embedder import Embedder

from infogain.resources.ontologies import language

class Test_RelationExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ont_language = language.ontology()
        cls.training = language.training()
        cls.testing = Document(content="Kieran can speak English rather well.")

        cls.testing.processKnowledge(cls.ont_language)

    @pytest.mark.skip
    def test_fit(self):
        """ Test the multiprocessing fitting process, ensure that it correctly fits and returns the model """
        
        embedder = Embedder()

        # Generate a document of relation datapoints
        def extract_speaks(document_set):
            document_speaks = Document("speaks")
            for document in document_set:
                embedder.train(document.words(cleaned=True))
                for point in document.datapoints():
                    if point.relation == "speaks":
                        document_speaks.addDatapoint(point)
            return document_speaks

        # Minimise the documents to speaks only
        training = extract_speaks(self.training)
        testing = extract_speaks([self.testing])

        # Embed the points
        for point in training.datapoints(): point.embedContext(embedder.sentence)
        for point in testing.datapoints(): point.embedContext(embedder.sentence)

        model = RelationModel("speaks")
        model = RelationExtractor._fit(model, training)

        testing.datapoints(model.predict(testing.datapoints()))

        for point in testing.datapoints(): self.assertAlmostEqual(point.prediction, 0.9, delta=0.1)

    @pytest.mark.skip
    def test_predict(self):

        extractor = RelationExtractor(ontology=language.ontology())
        extractor.fit(self.training)

        testing = RelationExtractor._predict(self.testing, extractor)

        for point in testing.datapoints(): self.assertAlmostEqual(point.prediction, 0.9, delta=0.1)
        