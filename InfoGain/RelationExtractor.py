from .Ontology import Ontology
from sklearn.neural_network import MLPRegressor

class RelationExtractor:
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self, ont: Ontology, k: int):
        """ Initialising the pool of relation classifiers and defining the method of learning
        that will take place.

        Params:
            ont - The ontology that defines the relationships of interest that can
                show up inside the text
            k - The number of words taken as context from either side of the 
                relation entities
        """
        self.ontology = ont

        network_shape = (k*2 + 40, 5)

        self.pool = { relation.name: MLPRegressor() }


        self.k = k
        pass

    def fit(self):
        """ Use the provided annotated document to provide training data to the
        regressors of """
        pass

    def predict(self):
        pass
    