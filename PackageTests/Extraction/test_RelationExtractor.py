import os, unittest

from InfoGain import Resources

from InfoGain.Knowledge import Ontology, Concept, Relation
from InfoGain.Documents import Document

from InfoGain.Extraction import RelationExtractor
from InfoGain.Resources import Language

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

        for point in alias_document.datapoints():
            print(point, "-", point.text)

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

"""
    def test_add_relation_extraction(self):
        pass

    def test_fit_relation_extraction(self):
        pass

    def test_predict_relation_extraction(self):
        pass

    def test_save_and_load_extraction(self):
        pass
"""