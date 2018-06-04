import os, unittest

from InfoGain.Knowledge import Ontology
from InfoGain.Documents import Document
from InfoGain import Resources

class Test_Document(unittest.TestCase):
    """ Test the functionality and inner workings of the generic prediction document """

    def setUp(self):
        self.contents = "When I generate a document in this manner, I want to ensure that the document "+\
        "object is created correctly. This is the initial test! Fingers crossed!!! Testing sentence end."

    def test_clean(self):

        sentenceMapping = {"Well this should work, I mean, I really hope that it does.":
            "well this should work i mean i really hope that it does"}

        for dirty, clean in sentenceMapping.items():
            self.assertEqual(Document.clean(dirty), clean)

        self.assertEqual(Document.clean(self.contents), "when i generate a document in this manner " +
        "i want to ensure that the document object is created correctly this is the initial test fingers crossed testing sentence end")

        self.assertEqual(Document.clean("Couldn't"), "could not")

        wordMapping = {"Kieran's": "kieran", "un-holy": "unholy", "word_spagetti": "word_spagetti",
                       "is": "is", "the": "the", "WORST": "worst", "Couldn't": "could not"}

        for dirty, clean in wordMapping.items():
            self.assertEqual(Document.clean(dirty), clean)


    def test_split(self):
        content = Document.split(self.contents, Document.SENTENCE)

        self.assertEqual(content, ["When I generate a document in this manner, I want to ensure that the document object is created correctly.",
                                   "This is the initial test!", 
                                   "Fingers crossed!!!",
                                   "Testing sentence end."])

    def test_removeWhitespace(self):
        self.assertEqual(Document.removeWhiteSpace("content     like this ? Should be fixed.. right   !"), "content like this? Should be fixed.. right!")

    def test_content_sentences(self):
        """ Generate a document with content that has been passed to the document """
        
        document = Document(content=self.contents)
        self.assertEqual(document.sentences(), ["When I generate a document in this manner, I want to ensure that the document object is created correctly.",
                                                "This is the initial test!", 
                                                "Fingers crossed!!!",
                                                "Testing sentence end."])


    def test_content_words(self):
        """ Test that a generated document correctly provides the words """

        document = Document(content=self.contents)
        self.assertEqual(document.words(), [["When","I","generate","a","document","in","this","manner,","I","want","to","ensure","that","the","document","object","is","created","correctly."],
                                            ["This", "is", "the", "initial", "test!"],
                                            ["Fingers", "crossed!!!"],
                                            ["Testing", "sentence", "end."]])

    def test_document_processKnowledge(self):
        """ Set that the datapoints are generated correctly. """

        language_content = "Luke has been living in England for about 10 years. When he first arrived he didn't know much"+\
        " English. Luke has been studying French, German and Spanish in a local community college."

        languages = Resources.Language.ontology()
        doc = Document(content=language_content)

        doc.processKnowledge(languages)

        # Check the total sum of datapoints
        self.assertEqual(len(doc), 5)

    def test_document_save_load(self):

        for path in Resources.TEXT_COLLECTIONS:
            document = Document(filepath=path)

            document.save(filename="./tempDocument.txt")
            newDocument = Document(filepath="./tempDocument.txt")

            self.assertEqual(document.text(), newDocument.text())

        os.remove("./tempDocument.txt")