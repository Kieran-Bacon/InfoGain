import os, unittest

from infogain.knowledge import Ontology, Concept, Relation
from infogain.artefact import Document, Datapoint
from infogain.extraction import RelationExtractor
from infogain.resources.ontologies import language

class Test_RelationExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = RelationExtractor(ontology=language.ontology(), min_count=1)
        self.extractor.fit(language.training())
    
    def test_add_concept_extraction(self):

        # Generate example documents
        luke_speaks_english = Document(name="luke", content="Luke speaks English")
        luke_san_speaks_english = Document(name="luke-san", content="Luke-san speaks English")
        natasha_speaks_english = Document(name="natasha", content="Natasha speaks English")

        # Process the example documents
        document_set = [luke_speaks_english, luke_san_speaks_english, natasha_speaks_english]
        processed_set = self.extractor.predict(document_set)

        # Show that only document luke has a datapoint as the other text representations were not found
        for document in processed_set:
            if document.name == "luke": self.assertTrue(document.datapoints())
            else:                       self.assertFalse(document.datapoints())

        # Expand the concepts text representations
        self.extractor.concept("Luke").alias.add("Luke-san")
        self.extractor.addConcept(Concept("Natasha", parents={"Person"}))

        # Predict the documents again - assert that all documents now have datapoints - concepts found
        processed_set = self.extractor.predict(document_set)
        for document in processed_set: self.assertTrue(document.datapoints())

    def test_add_relation_extraction(self):
        """ Test that an added relationship is generated correctly """

        # Creating the relationship friends with
        person = self.extractor.concept("Person")  # Collecting the person concept for relation binding
        Friends = Relation({person}, "friendsWith", {person})  # Creating the relation object
        self.extractor.addRelation(Friends)  # Adding the relationship to the relation extractor

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
        test = self.extractor.predict(test)[0]

        self.assertEqual(len(test), 4)  # 2 from inform, 2 from friendsWith
        count = 0
        for datapoint in test.datapoints(): count += 1 if datapoint.relation == "friendsWith" else 0
        self.assertEqual(count, 2)