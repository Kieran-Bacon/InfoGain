from .Ontology import Ontology
from .Document import TrainingDocument
from sklearn.neural_network import MLPClassifier

from gensim.models import Word2Vec

class RelationExtractor(Ontology):
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self, name=None, filepath=None, ontology=None, k=20):
        """ Initialising the pool of relation classifiers and defining the method of learning
        that will take place.

        Params:
            ont - The ontology that defines the relationships of interest that can
                show up inside the text
            k - The number of words taken as context from either side of the 
                relation entities
        """

        self.name = name

        if filepath:
            # Call ontology constructor
            Ontology.__init__(self, name=name, filepath=filepath)

        elif ontology:
            # Convert ontology into a relation extractor instance
            ontologyClone = ontology.clone()
            self.name = ontologyClone.name if not ontologyClone is None else name
            self._concepts = ontologyClone._concepts
            self._relations = ontologyClone._relations
            self._facts = ontologyClone._facts

        self.WordEmbedding = None
        self.ensemble = {rel:RelationModel() for rel in ontology.relations()}
        
        self._trainingCorpus = set()

    def _trainWordEmbeddings(self):
        pass
        sentences = [ doc.text.split() for doc in self._trainingCorpus]
        #sentences = [point.text for doc in annotated_documents for point in doc.datapoints()]
        self.WordModel = Word2Vec(sentences, min_count=1, size=300)

    def _sentenceEmbedding(self, datapoint):
        pass

    def fit(self, training_documents: [TrainingDocument] ) -> None:
        """ Use the provided annotated document to provide training data to the
        regressors of
        
        Params:
            - annotations: A single file, or a list of file paths to training documents
        """

        # Allow single or list of documents, convert training documents
        if isinstance(training_documents, TrainingDocument):
            training_documents = [training_documents]

        for document in training_documents:

            # Record training document
            self._trainingCorpus.add(document)

            # Extract text representations and save them to the ontology
            [self.concept(con).addRepr(t) for con, text in document.concepts() for t in text]

        # Train the word embedding method
        self._trainWordEmbeddings()

        # Train the relation models
        modelData = {rel: [] for rel in self.ensemble.keys()}
        for document in training_documents:
            for point in document.datapoints():
                modelData[point.relation].append(self._sentenceEmbedding(point))

        [self.ensemble[rel].fit(data) for rel, data in modelData.items()]

    def predict(self):
        pass

class RelationModel:
    """ The model the learns the sentence embeddings for a particular relationship """

    def fit(self, datapoints):

        # Cross validation in here
        pass

    def predict(self, point):
        pass