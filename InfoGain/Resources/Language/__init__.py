import os
ROOT = os.path.dirname(os.path.realpath(__file__))

from ...Knowledge import Ontology
from ...Documents import Document

class DomainResources:

    ontologyObj = None
    trainingSet = None
    trainingSize = None
    testingSet = None
    testingSize = None

    @classmethod
    def ontology(cls, get_path=False) -> Ontology:

        if cls.ontologyObj is None:

            cls.ontologyObj = Ontology(filepath=os.path.join(ROOT, "ontology.json"))
            return cls.ontologyObj

        if get_path:
            return cls.ontologyObj, os.path.join(ROOT, "ontology.json")
        return cls.ontologyObj

    @classmethod
    def training(cls, num_of_docs=None) -> Document:

        if cls.trainingSet is None or num_of_docs != cls.trainingSize:

            files = os.listdir(os.path.join(ROOT, "training"))
            if num_of_docs: files = files[:num_of_docs]
            
            cls.trainingSet = [Document(filepath=os.path.join(ROOT, "training", name)) for name in files]
            cls.trainingSize = num_of_docs

        return cls.trainingSet

    @classmethod
    def testing(cls, num_of_docs=None) -> Document:

        if cls.testingSet is None or num_of_docs != cls.testingSize:

            files = os.listdir(os.path.join(ROOT, "testing"))
            if num_of_docs: files = files[:num_of_docs]

            cls.testingSet = [Document(filepath=os.path.join(ROOT, "testing", name)) for name in files]
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
