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

    def __eq__(self, other):
        if isinstance(other, Datapoint):

            return (self.text == other.text and\
                    self.domain == other.domain and\
                    self.target == other.target and\
                    self.relation == other.relation and\
                    self.annotation == other.annotation)

        return self.text == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.text)

    def __init__(self, ontology:Ontology, data: dict):
        """ Taking a dictionary representation of a datapoint. Assign the information to object
        variables for convience.

        Params:
            - data: A dictionary of the datapoint information.
        """

        # Link the object to the ontology structures
        self.domain = ontology.concept(data["domain"]["concept"])
        self.target = ontology.concept(data["target"]["concept"])
        self.relation = ontology.relation(data["relation"])

        self.text = data["text"]

        self.lContext = data["context"]["left"]
        self.mContext = data["context"]["middle"]
        self.rContext = data["context"]["right"]

        self.annotation = data["annotation"]

