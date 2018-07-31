import os, unittest

from InfoGain import Resources

from InfoGain.Knowledge import Ontology
from InfoGain.Documents import Document

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

        wordMapping = {"Kieran's": "kieran", "un-holy": "un holy", "word_spagetti": "word_spagetti",
                       "is": "is", "the": "the", "WORST": "worst", "Couldn't": "could not"}

        for dirty, clean in wordMapping.items():
            self.assertEqual(Document.clean(dirty), clean)

        Document.split(Document.clean("Luke can speak English rather well, but Luke doesn't live in England."), Document.SENTENCE)


    def test_split(self):
        content = Document.split(self.contents, Document.SENTENCE)

        self.assertEqual(content, ["When I generate a document in this manner, I want to ensure that the document object is created correctly.",
                                   "This is the initial test!", 
                                   "Fingers crossed!!!",
                                   "Testing sentence end."])

        content = Document.split("Luke can speak English rather well, but Luke doesn't live in England.", Document.SENTENCE)
        
        self.assertEqual(content, ["Luke can speak English rather well, but Luke doesn't live in England."])

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

        languages = Resources.Ontologies.Language.ontology()
        doc = Document(content=language_content)

        doc.processKnowledge(languages)

        # Check the total sum of datapoints
        self.assertEqual(len(doc), 5)

        document = Document(content="Luke can speak English rather well, but Luke doesn't live in England.")
        document.processKnowledge(languages)

        self.assertEqual(len(document), 7)

    def test_alias_process_knowledge(self):
        """ Check that the document doesn't match on alias when it shouldn't and does when it should """

        # Collect an ontology
        ontology = Resources.Ontologies.Language.ontology()

        # Generate a document and process the knowledge
        test = Document(content="Luke-san speaks English")
        test.processKnowledge(ontology)

        # Assert that no datapoints were produced
        self.assertEqual(len(test.datapoints()), 0)

        # Add the alias
        ontology.concept("Luke").alias.add("Luke-san")
        test.processKnowledge(ontology)

        # Assert alias is found
        self.assertEqual(len(test), 1)

    def test_regular_expression_alias(self):
        """ Test that if a alias is a regular expression it will work correctly """

        # Collect an ontology
        ontology = Resources.Ontologies.Language.ontology()

        # Add an alias
        ontology.concept("Kieran").alias.add(r"\d+:\d+:\d+ date")

        # Generate the test string and process it
        document = Document(content="18:09:2018 date speaks English")
        document.processKnowledge(ontology)
        
        # Assert that the regex works as expected
        self.assertEqual(len(document), 1)
        self.assertEqual(document.datapoints()[0].domain["text"], "18:09:2018 date")

    def test_datapoint_reproducement(self):
        """ For a datapoint that is processed and found within the text, One should be able to
        create a new document with that content and extract the same datapoint """

        original = Document(content="Kieran is the best English speaker that has ever lived.")
        original.processKnowledge(Resources.Ontologies.Language.ontology())

        self.assertEqual(len(original.datapoints()), 1)

        new_document = Document(content=original.text())
        new_document.processKnowledge(Resources.Ontologies.Language.ontology())

        self.assertEqual(len(new_document.datapoints()), 1)

        self.assertEqual(set(original.datapoints()),set(new_document.datapoints()))

    def test_document_save_load(self):

        for path in Resources.TEXT_COLLECTIONS:
            document = Document(filepath=path)

            document.save(filename="./tempDocument.txt")
            newDocument = Document(filepath="./tempDocument.txt")

            self.assertEqual(document.text(), newDocument.text())

        os.remove("./tempDocument.txt")