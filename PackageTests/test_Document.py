import os, unittest
from . import DOCUMENTS, ONTOLOGIES, PATHS

from InfoGain import Ontology, Document

class Test_Document(unittest.TestCase):
    """ Test the functionality and inner workings of the generic prediction document """

    def test_content_load(self):
        """ Generate a document with content that has been passed to the document """
        contents = "When I generate a document in this manner, I want to ensure that the document "+\
        "object is created correctly. This is the initial test! Fingers crossed!!! Testing sentence end."

        cleanedContents = "when i generate a document in this manner i want to ensure that the " +\
        "document object is created correctly this is the initial test fingers crossed testing sentence end"

        document = Document(content=contents)

        # TODO: This needs to be finished.

    def test_document_processKnowledge(self):
        """ Set that the datapoints are generated correctly. """

        language_content = "Luke has been living in England for about 10 years. When he first arrived he didn't know much"+\
        " English. Luke has been studying French, German and Spanish in a local community college."

        languages = Ontology(filepath=PATHS["language"]["ontology"])
        doc = Document(content=language_content)

        doc.processKnowledge(languages)

        self.assertEqual(len(doc.datapoints()), 5)