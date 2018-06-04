import unittest

from InfoGain.Documents import Document, score
from InfoGain.Resources import Language

class Test_Score(unittest.TestCase):

    def test_score_function(self):

        ont = Language.ontology()
        testing = Language.testing()
        [doc.processKnowledge(ont) for doc in testing]

        corpus, documents = score(ont, testing)

        self.assertEqual(corpus["recall"], 1.0)