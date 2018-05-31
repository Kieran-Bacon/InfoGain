import os
ROOT = os.path.dirname(os.path.realpath(__file__))

class Medicine:

    ontologyObj = None
    trainingSet = None
    trainingSize = None
    testingSet = None
    testingSize = None

    @classmethod
    def ontology(cls, get_path=False):

        if cls.ontologyObj is None:

            from InfoGain.Knowledge import Ontology
            cls.ontologyObj = Ontology(filepath=os.path.join(ROOT, "ontology.json"))
            return cls.ontologyObj

        if get_path:
            return cls.ontologyObj, os.path.join(ROOT, "ontology.json")
        return cls.ontologyObj

    @classmethod
    def training(cls, num_of_docs=None):

        if cls.trainingSet is None or num_of_docs != cls.trainingSize:

            import os
            from InfoGain.Documents import TrainingDocument

            files = os.listdir(os.path.join(ROOT, "training"))
            if num_of_docs: files = files[:num_of_docs]
            
            cls.trainingSet = [TrainingDocument(filepath=os.path.join(ROOT, "training", name)) for name in files]
            cls.trainingSize = num_of_docs

        return cls.trainingSet

    @classmethod
    def testing(cls, num_of_docs=None):

        if cls.testingSet is None or num_of_docs != cls.testingSize:

            import os
            from InfoGain import Document

            files = os.listdir(os.path.join(ROOT, "testing"))
            if num_of_docs: files = files[:num_of_docs]

            cls.testingSet = [Document(filepath=os.path.join(ROOT, "testing", name)) for name in files]
            cls.testingSize = num_of_docs

        return cls.testingSet
