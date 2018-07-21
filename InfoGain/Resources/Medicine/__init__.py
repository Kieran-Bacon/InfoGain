import os
ROOT = os.path.dirname(os.path.realpath(__file__))

from ...Knowledge import Ontology
from ...Documents import Document

class Medicine:
    """ Class that holds and represents a domain of information and provides convenient functions to
    be able to interact with that information. Acts as a single class """

    __ontologyObj = None
    __trainingSet = None
    __trainingSize = None
    __testingSet = None
    __testingSize = None

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

        if cls.__ontologyObj is None:

            cls.__ontologyObj = Ontology(filepath=os.path.join(ROOT, "ontology.json"))
            return cls.__ontologyObj

        if get_path:
            return cls.__ontologyObj, os.path.join(ROOT, "ontology.json")
        return cls.__ontologyObj

    @classmethod
    def training(cls, num_of_docs: int=None) -> [Document]:
        """ Load and store training documents for the domain

        Params:
            num_of_documents (int) - The number of training documents to be returned
        
        Returns:
            [Document] - A collection of training documents for this domain
        """

        if cls.__trainingSet is None or num_of_docs != cls.__trainingSize:

            files = os.listdir(os.path.join(ROOT, "training"))
            files.remove("__init__.py")  # Remove the package indicator from the list

            if num_of_docs: files = files[:num_of_docs]          
            cls.__trainingSet = [Document(filepath=os.path.join(ROOT, "training", name))
                for name in files]
            cls.__trainingSize = num_of_docs

        return cls.__trainingSet

    @classmethod
    def testing(cls, num_of_docs: int=None) -> Document:
        """ Load and store un-annotated documents from the domain to act as documents to predict
        on

        Params:
            num_of_docs (int) - The number of documents to return from the collection
        
        Returns:
            [Document] - The collection of documents to predict upon
        """

        if cls.__testingSet is None or num_of_docs != cls.__testingSize:

            files = os.listdir(os.path.join(ROOT, "testing"))
            files.remove("__init__.py")  # Remove the package indicator from the list
            
            if num_of_docs: files = files[:num_of_docs]

            cls.__testingSet = [Document(filepath=os.path.join(ROOT, "testing", name))
                for name in files]
            cls.__testingSize = num_of_docs

        return cls.__testingSet

    @classmethod
    def reset(cls):
        """ Reset the contents of this ontology """
        cls.__ontologyObj = None
        cls.__trainingSet = None
        cls.__trainingSize = None
        cls.__testingSet = None
        cls.__testingSize = None
