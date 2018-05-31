import os, unittest, json

import InfoGain.Documents.DocumentOperations as DO

class Test_DocumentOperations(unittest.TestCase):
    """ Test the convient supportive functions used by the document objects. """

    def test_cleanSentence(self):
        sentenceMapping = {"Well this should work, I mean, I really hope that it does.":
            "well this should work i mean i really hope that it does"}

        for dirty, clean in sentenceMapping.items():
            self.assertEqual(DO.cleanSentence(dirty), clean)

    def test_cleanWord(self):

        wordMapping = {"Kieran's": "kieran", "un-holy": "un-holy", "word_spagetti": "word_spagetti",
            "is": "is", "the": "the", "WORST": "worst"}

        for dirty, clean in wordMapping.items():
            self.assertEqual(DO.cleanWord(dirty), clean.split())


if __name__ == "__main__":
    unittest.main()