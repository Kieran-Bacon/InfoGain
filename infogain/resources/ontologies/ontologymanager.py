import os
from ...serialisers import SerialiseFactory
from ...knowledge import Ontology
from ...artefact import Document

ROOT = os.path.dirname(os.path.realpath(__file__))

class OntologyManager:

    def __init__(self, filepath: str):
        self.directory = filepath

        self.path_ontology = os.path.join(self.directory, "ontology.json")

        self.loaded_training = {}
        self.loaded_testing = {}

    def ontology(self) -> Ontology:
        """ Load and return the language ontology, keep the ontology loaded for quick return if
        promted again

        Params:
            get_path (str) - A toggle to inform where the path to the ontology should be returned

        Returns:
            Ontology - the ontology object of the domain
            str - The path, may be returned
            """
        return SerialiseFactory("json").load(self.path_ontology)

    def training(self, num_of_docs: int = None) -> [Document]:
        """ Load and store training documents for the domain

        Params:
            num_of_documents (int) - The number of training documents to be returned

        Returns:
            [Document] - A collection of training documents for this domain
        """

        trainingFiles = os.listdir(os.path.join(self.directory, "training"))
        trainingFiles.remove("__init__.py")
        if "__pycache__" in trainingFiles: trainingFiles.remove("__pycache__")

        if num_of_docs: trainingFiles = trainingFiles[:num_of_docs]

        return [Document(filepath=os.path.join(self.directory, "training", filename))
            for filename in trainingFiles]

    def testing(self, num_of_docs: int = None) -> [Document]:
        """ Load and store un-annotated documents from the domain to act as documents to predict
        on

        Params:
            num_of_docs (int) - The number of documents to return from the collection

        Returns:
            [Document] - The collection of documents to predict upon
        """

        testingFiles = os.listdir(os.path.join(self.directory, "testing"))
        testingFiles.remove("__init__.py")
        if "__pycache__" in testingFiles: testingFiles.remove("__pycache__")

        if num_of_docs: testingFiles = testingFiles[:num_of_docs]

        return [Document(filepath=os.path.join(self.directory, "testing", filename))
            for filename in testingFiles]

language = OntologyManager(filepath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "language"))
school = OntologyManager(filepath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "school"))