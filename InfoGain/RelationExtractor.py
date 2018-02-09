from .Ontology import Ontology
#from .Language import DocumentDecoder, Document
from sklearn.neural_network import MLPClassifier

class RelationExtractor:
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self, ontology: Ontology, k: int):
        """ Initialising the pool of relation classifiers and defining the method of learning
        that will take place.

        Params:
            ont - The ontology that defines the relationships of interest that can
                show up inside the text
            k - The number of words taken as context from either side of the 
                relation entities
        """
        self.ontology = ontology

    def fit(self, Annotated_Documents: [str] ) -> None:
        """ Use the provided annotated document to provide training data to the
        regressors of
        
        Params:
            - Annotated_Documents: A single file, or a list of file paths to training documents 
        """

        


        pass

    def predict(self):
        pass

class Datapoint:

    def __init__(self, domain, target, relation, lc, mc, rc, classification):
        self.domain = domain
        self.target = target
        self.relation = relation
        self.lContext = lContext
        self.mContext = mContext
        self.rContext = rContext
        self.classification = classification