import unittest

from infogain.knowledge import abstract, Rule
from infogain import knowledge
from infogain.cognition import InferenceEngine

class Language(abstract.Ontology):

    class Person(abstract.Concept): pass

    class Country(abstract.Concept): pass
    class England(Country):
        category = "static"

    class Language(abstract.Concept): pass
    class English(Language):
        properties = {
            "origin": "latin"
        }
        category = "static"

    class bornIn(abstract.Relation):
        domains = [["Person"]]
        targets = [["Country"]]

    class livesIn(abstract.Relation):
        domains = [["Person"]]
        targets = [["Country"]]

    class speaks(abstract.Relation):
        domains = [["Person", "Country"]]
        targets = [["Language"]]

        rules = [
            abstract.Rule("Person", "Language", 60,
                conditions = [
                    abstract.Condition("%=livesIn=#Country", 100),
                    abstract.Condition("#Country=speaks=@", 100)
                ]
            ),
            abstract.Rule("England", "English", 80)
        ]

    class informs(abstract.Relation):
        domains = [["Person"]]
        targets = [["Person"]]
        differ = True

class Test_abstract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ontology = Language.build()

    def test_abstractConceptDefinition(self):
        self.assertEqual(knowledge.Concept("Person"), self.ontology.concept("Person"))
        self.assertEqual(self.ontology.concept("English").properties["origin"], "latin")

    def test_abstractConceptInstanceDefinition(self):
        self.fail()

    def test_abstractRelation(self):
        self.fail()

    def test_Inference(self):

        engine = InferenceEngine(ontology=self.ontology)

        kieran = engine.concept("Person").instance("Kieran")

        engine.addInstance(kieran)

        livesIn = engine.relation("livesIn")
        livesIn.addRule(Rule(kieran, engine.instance("England"), 82))

        self.assertGreater(
            engine.inferRelation(engine.instance("Kieran"), "speaks", engine.instance("English")),
            35
        )
