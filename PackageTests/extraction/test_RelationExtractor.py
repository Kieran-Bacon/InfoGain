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

        luke_speaks_english = Document(name="luke", content="Luke speaks English")
        luke_san_speaks_english = Document(name="luke-san", content="Luke-san speaks English")
        natasha_speaks_english = Document(name="natasha", content="Natasha speaks English")

        document_set = [luke_speaks_english, luke_san_speaks_english, natasha_speaks_english]

        processed_set = self.extractor.predict(document_set)

        for document in processed_set:
            if document.name == "luke":
                self.assertEqual(len(document), 1)
            else:
                self.assertEqual(len(document), len(document.text()))

        return

        self.extractor.predict([luke_speaks_english, luke_san_speaks_english, natasha_speaks_english])

        # Assert the normal behaviour 
        self.assertEqual(len(document), len(document.text()))
        self.assertEqual(len(alias_document.datapoints()), 0)
        self.assertEqual(len(new_document.datapoints()), 0)

        luke = self.extractor.concept("Luke")
        luke.alias.add("Luke-san")

        natasha = Concept("Natasha", parents={"Person"})
        self.extractor.addConcept(natasha)

        new_document = self.extractor.predict([new_document])[0]
        self.assertEqual(len(new_document), 1)
        self.assertEqual(len(alias_document), 0)

        alias_document = self.extractor.predict([alias_document])[0]
        self.assertEqual(len(alias_document), 1)



        testing_documents = self.extractor.predict([alias_document, new_document])

        # Assert the new datapoints
        for doc in testing_documents:
            self.assertEqual(len(doc), 1)

    def test_add_relation_extraction(self):
        """ Test that an added relationship is generated correctly """

        # Creating the relationship friends with
        person = self.extractor.concept("Person")  # Collecting the person concept for relation binding
        Friends = Relation({person}, "friendsWith", {person})  # Creating the relation object
        print(Friends._between)
        print(Friends.between(self.extractor.concept("Kieran"), self.extractor.concept("Luke")))
        self.extractor.addRelation(Friends)  # Adding the relationship to the relation extractor

        # Generate some training points for this relationship
        points = [
            Datapoint({"domain":{"concept":"Kieran", "text":"Kieran"}, "relation":"friendsWith", "target":{"concept":"Luke", "text":"Luke"}, "context":{"left":"", "middle":" is a good friends with ", "right":"."}, "text":"Kieran is a good friend with Luke.", "annotation":1}),
            Datapoint({"domain":{"concept":"Kieran", "text":"Kieran"}, "relation":"friendsWith", "target":{"concept":"Luke", "text":"Luke"}, "context":{"left":"", "middle":"has been good friends with", "right":" for a long time."}, "text":"Kieran has always been good friends with Luke", "annotation":1}),
            Datapoint({"domain":{"concept":"Kieran", "text":"Kieran"}, "relation":"friendsWith", "target":{"concept":"Luke", "text":"Luke"}, "context":{"left":"", "middle":" only recently became good friends with", "right":"."}, "text":"Kieran has only recently became good friends with Luke.", "annotation":1})
        ]
        training = Document()
        training.datapoints(points)

        # Train the model
        self.extractor.fit(training)

        # Create a test document and predict on it
        test = Document(content="Kieran has always been a friend of Luke's")
        test = self.extractor.predict(test)[0]

        print(self.extractor.relation("inform"))

        for dp in test.datapoints():
            print(dp)

        # Assert that two datapoints can be found within the text
        self.assertEqual(len(test), 4)  # 2 from inform, 2 from friendsWith

"""
    def test_fit_relation_extraction(self):
        pass

    def test_predict_relation_extraction(self):
        pass

    def test_save_and_load_extraction(self):
        pass
"""