import os, unittest, json
from . import DOCUMENTS, ONTOLOGIES

from InfoGain import Ontology, Document, TrainingDocument
from InfoGain.Document import cleanSentence, cleanWord

class Test_Document(unittest.TestCase):

    def test_cleanSentence(self):
        sentenceMapping = {"Well this should work, I mean, I really hope that it does.":
            "well this should work i mean i really hope that it does"}

        for dirty, clean in sentenceMapping.items():
            self.assertEqual(cleanSentence(dirty), clean)

    def test_cleanWord(self):

        wordMapping = {"Kieran's": "kieran", "un-holy": "un-holy", "word_spagetti": "word_spagetti",
            "is": "is", "the": "the", "WORST": "worst"}

        for dirty, clean in wordMapping.items():
            self.assertEqual(cleanWord(dirty), clean)


if __name__ == "__main__":
    unittest.main()