import os
from types import ModuleType
ROOT = os.path.dirname(os.path.realpath(__file__))

from ...Knowledge import Ontology
from ...Documents import Document

class DomainResources:
    """ Class that holds and represents a domain of information and provides convenient functions to
    be able to interact with that information. Acts as a single class """

    ontologyObj = None
    trainingSet = None
    trainingSize = None
    testingSet = None
    testingSize = None

    @classmethod
    def ontology(cls, get_path: bool=False) -> Ontology:
        """ Load and return the language ontology, keep the ontology loaded for quick return if
        promted again 
        
        Params:
            get_path (str) - A toggle to inform where the path to the ontology should be returned
        
        Returns:
            Ontology - the ontology object of the domain
            str - The path, may be returned
        """

        if cls.ontologyObj is None:

            cls.ontologyObj = Ontology(filepath=os.path.join(ROOT, "ontology.json"))
            return cls.ontologyObj

        if get_path:
            return cls.ontologyObj, os.path.join(ROOT, "ontology.json")
        return cls.ontologyObj

    @classmethod
    def training(cls, num_of_docs: str=None) -> [Document]:
        """ Load and store training documents for the domain

        Params:
            num_of_documents (int) - The number of training documents to be returned
        
        Returns:
            [Document] - A collection of training documents for this domain
        """

        if cls.trainingSet is None or num_of_docs != cls.trainingSize:

            files = os.listdir(os.path.join(ROOT, "training"))
            if num_of_docs: files = files[:num_of_docs]          
            cls.trainingSet = [Document(filepath=os.path.join(ROOT, "training", name))
                for name in files]
            cls.trainingSize = num_of_docs

        return cls.trainingSet

    @classmethod
    def testing(cls, num_of_docs=None) -> Document:
        """ Load and store un-annotated documents from the domain to act as documents to predict
        on

        Params:
            num_of_docs (int) - The number of documents to return from the collection
        
        Returns:
            [Document] - The collection of documents to predict upon
        """

        if cls.testingSet is None or num_of_docs != cls.testingSize:

            files = os.listdir(os.path.join(ROOT, "testing"))
            if num_of_docs: files = files[:num_of_docs]

            cls.testingSet = [Document(filepath=os.path.join(ROOT, "testing", name))
                for name in files]
            cls.testingSize = num_of_docs

        return cls.testingSet

    @classmethod
    def reset(cls):
        """ Reset the contents of this ontology """
        cls.ontologyObj = None
        cls.trainingSet = None
        cls.trainingSize = None
        cls.testingSet = None
        cls.testingSize = None
