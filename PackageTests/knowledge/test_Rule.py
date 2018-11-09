import unittest, pytest
from infogain import knowledge

class Test_Rule(unittest.TestCase):

    def setUp(self):

        # Concepts for the rules
        self.country, self.language = knowledge.Concept("Country"), knowledge.Concept("Language")
        self.england, self.english = self.country.instance("England"), self.language.instance("English")

        # Fact applying rule for two instances only
        self.england_speaks_english = knowledge.Rule(self.england, self.english, 80)

        # Condition based rule
        conditions = [
            knowledge.Condition("%.age.graph(x > 10)", 24)
        ]

        self.country_speaks_language = knowledge.Rule(self.country, self.language, 80, conditions)

    def test_applies_raises_when_not_equal(self):

        with pytest.raises(ValueError):
            self.country_speaks_language.applies("string", knowledge.Concept("A concept"))

        with pytest.raises(ValueError):
            self.country_speaks_language.applies(knowledge.Concept(""), knowledge.Instance(""))

    def test_applies_works_for_rules_with_concepts(self):

        self.assertTrue(self.country_speaks_language.applies(self.country, self.language))
        self.assertTrue(self.country_speaks_language.applies(self.england, self.english))

    def test_applies_works_for_rules_with_instances(self):

        self.assertFalse(self.england_speaks_english.applies(self.country, self.language))
        self.assertTrue(self.england_speaks_english.applies(self.england, self.english))

    def test_applies_works_with_strings(self):

        self.assertTrue(self.country_speaks_language.applies("Country", "Language"))
        self.assertFalse(self.country_speaks_language.applies("England", "English"))
        self.assertTrue(self.england_speaks_english.applies("England", "English"))
        self.assertFalse(self.england_speaks_english.applies("Country", "Language"))

    def test_hasConditions(self):
        self.assertTrue(self.country_speaks_language.hasConditions())


    def test_minimise(self):

        
        minimised = {
            "domains": ["England"],
            "targets": ["English"],
            "confidence": 80,
        }

        self.assertEqual(minimised, self.england_speaks_english.minimise())

        minimised = {
            "domains": ["Country"],
            "targets": ["Language"],
            "confidence": 80,
            "conditions":[
                {"logic": "%.age.graph(x > 10)", "salience": 24}
            ]
        }

        self.assertEqual(minimised, self.country_speaks_language.minimise())

