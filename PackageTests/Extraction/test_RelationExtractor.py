import os, unittest

from InfoGain import Resources

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document, Datapoint

from InfoGain.Extraction import RelationExtractor
from InfoGain.Resources.Ontologies import Language

from InfoGain import Resources

class Test_RelationExtractor(unittest.TestCase):

    def setUp(self):

        self.extractor = RelationExtractor(ontology=Language.ontology(), min_count=1)
        self.extractor.fit(Language.training())
    
    def test_add_concept_extraction(self):

        document = Document(content="Luke speaks English")
        alias_document = Document(content="Luke-san speaks English")
        new_document = Document(content="Natasha speaks English")

        self.extractor.predict([document, alias_document, new_document])

        # Assert the normal behaviour 
        self.assertEqual(len(document), 1)
        self.assertEqual(len(alias_document.datapoints()), 0)
        self.assertEqual(len(new_document.datapoints()), 0)

        luke = self.extractor.concept("Luke")
        luke.alias.add("Luke-san")

        natasha = Concept("Natasha", parents={"Person"})
        self.extractor.addConcept(natasha)

        self.extractor.predict([alias_document, new_document])

        # Assert the new datapoints
        self.assertEqual(len(alias_document), 1)
        self.assertEqual(len(new_document), 1)


    def test_add_relation_extraction(self):
        """ Test that an added relationship is generated correctly """

        # Creating the relationship friends with
        person = self.extractor.concept("Person")  # Collecting the person concept for relation binding
        Friends = Relation({person}, "friendsWith", {person})  # Creating the relation object
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
        self.extractor.predict(test)

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