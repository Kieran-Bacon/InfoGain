import unittest
from infogain import knowledge

class Test_Rule(unittest.TestCase):

    def setUp(self):

        # Concepts for the rules
        country, language = knowledge.Concept("Country"), knowledge.Concept("Language")
        england, english = knowledge.Concept("England", {country}), knowledge.Concept("English", {language})

        # Fact applying rule
        self.england_speaks_english = knowledge.Rule(england, "speaks", english, 80)

        # Condition based rule
        conditions = [
            {"logic": "%.age->graph(x > 10)", "salience": 24}
        ]

        self.country_speaks_language = knowledge.Rule({country}, "speaks", {language}, 80, conditions)

    def test_minimise(self):

        
        minimised = {
            "domains": ["England"],
            "targets": ["English"],
            "confidence": 80,
            "relation": "speaks"
        }

        self.assertEqual(minimised, self.england_speaks_english.minimise())

        minimised = {
            "domains": ["Country"],
            "targets": ["Language"],
            "relation": "speaks",
            "confidence": 80,
            "conditions":[
                {"logic": "%.age->graph(x > 10)", "salience": 24}
            ]
        }

        self.assertEqual(minimised, self.country_speaks_language.minimise())

