import os, unittest, pytest

from infogain.artefact import Document
from infogain.knowledge import Concept
from infogain.extraction import ExtractionEngine, ExtractionRelation
from infogain.extraction.embedder import Embedder

from infogain.resources.ontologies import language

class Test_ExtractionEngine(unittest.TestCase):

    def setUp(self):
        self.extractor = ExtractionEngine(ontology=language.ontology())
        self.training = language.training()
        self.testing = Document(content="Kieran can speak English rather well.")

    def test_fit_predict(self):

        # Fit on the training data
        self.extractor.fit(self.training)

        # Assert that some of the relations have been fit
        self.assertTrue(any(r.fitted for r in self.extractor.relations()))

        # Predict on the testing data
        self.extractor.predict(self.testing)

        # Assert that there are datapoints for the testing document and they they are high accuracy
        self.assertTrue(len(self.testing.datapoints()) > 0)
        for point in self.testing.datapoints():
            self.assertAlmostEqual(point.prediction, 0.9, delta=0.1)

    def test_addingConcept_fit_predict(self):

        # Train the extractor
        self.extractor.fit(self.training)

        # Generate example documents
        luke_speaks_english = Document(name="luke", content="Luke speaks English")
        luke_san_speaks_english = Document(name="luke-san", content="Luke-san speaks English")
        natasha_speaks_english = Document(name="natasha", content="Natasha speaks English")

        # Process the example documents
        document_set = [luke_speaks_english, luke_san_speaks_english, natasha_speaks_english]
        processed_set = [self.extractor.predict(doc) for doc in document_set]

        # Show that only document luke has a datapoint as the other text representations were not found
        for document in processed_set:
            if document.name == "luke": self.assertTrue(document.datapoints())
            else:                       self.assertFalse(document.datapoints())

        # Expand the concepts text representations
        self.extractor.concepts["Luke"].aliases.add("Luke-san")
        self.extractor.concepts.add(Concept("Natasha", parents={"Person"}))

        # Predict the documents again - assert that all documents now have datapoints - concepts found
        processed_set = [self.extractor.predict(doc) for doc in document_set]
        for document in processed_set: self.assertTrue(document.datapoints())

    def test_addingRelation_fit_predict(self):

            # Creating the relationship friends with
            person = self.extractor.concepts["Person"]  # Collecting the person concept for relation binding
            Friends = ExtractionRelation({person}, "friendsWith", {person})  # Creating the relation object
            self.extractor.relations.add(Friends)  # Adding the relationship to the relation extractor

            document_set = [
                Document(content="Kieran is a good friend of Luke."),
                Document(content="Kieran has always been good friends with Luke"),
                Document(content="Kieran has only recently became good friends with Luke.")
            ]

            for doc in document_set: doc.processKnowledge(self.extractor)
            for datapoint in [point for document in document_set for point in document.datapoints()]:
                datapoint.annotation = 1

            self.extractor.fit(document_set)

            # Create a test document and predict on it
            test = Document(content="Kieran has always been a friend of Luke's")
            test = self.extractor.predict(test)

            self.assertEqual(len(test), 4)  # 2 from inform, 2 from friendsWith
            count = 0
            for datapoint in test.datapoints(): count += 1 if datapoint.relation == "friendsWith" else 0
            self.assertEqual(count, 2)