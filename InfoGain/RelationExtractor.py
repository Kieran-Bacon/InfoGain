from .Ontology import Ontology
from .Document import Document, TrainingDocument

import numpy
from sklearn.neural_network import MLPClassifier
from gensim.models import Word2Vec

class RelationExtractor(Ontology):
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self, name=None, filepath=None, ontology=None, k=20, embeddingSize=300):
        """ Initialising the pool of relation classifiers and defining the method of learning
        that will take place.

        Params:
            ont - The ontology that defines the relationships of interest that can
                show up inside the text
            k - The number of words taken as context from either side of the 
                relation entities
        """

        self.name = name
        self.contextWindow = k
        self.embeddingSize = embeddingSize

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
        self.ensemble = {rel.name:RelationModel() for rel in self.relations()}
        
        self._trainingCorpus = set()

    def _trainWordEmbeddings(self):
        """ Train the word embedding model on the words provided by the training documents """
        sentences = [sentence for doc in self._trainingCorpus for sentence in doc.sentences()]
        self.wordModel = Word2Vec(sentences, min_count=1, size=self.embeddingSize)

    def _embedSentence(self, sentence: str) -> numpy.array:
        """ Convert a sentence of variable length into a sentence embedding using the learn word
        embeddings"""

        embedding = numpy.zeros(self.embeddingSize)
        words = sentence.split()

        def pf(index: int) -> float:
            """ Return the output of a monotonic function as to reduce traling word embeddings """
            # TODO: Change function to something meaningful with support from someone
            return -numpy.log((index+1)/(len(words)+1))

        for index, word in enumerate(words):
            try:
                embedding += pf(index)*self.wordModel.wv[word]
            except:
                print("Word not about of vocabulary ::", word)

        return embedding

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
            [self.concept(name).addRepr(text) for name, textRepr in document.concepts() for text in textRepr]

        # Train the word embedding method
        self._trainWordEmbeddings()

        # Train the relation models
        modelData = {rel: [] for rel in self.ensemble.keys()}
        for document in training_documents:
            for point in document.datapoints():
                # Pass the embedding function to the point to embed its context
                point.embedContext(self._embedSentence)
                # Store the embedded point
                try:
                    modelData[point.relation].append(point)
                except:
                    print(modelData.keys())
                    assert(point.relation in self._relations)
                    assert(point.relation in modelData)

                    print("relation not found ::", point.relation)
                    print(point.text)

        [self.ensemble[rel].fit(data) for rel, data in modelData.items()]
        
    def predict(self, documents: [Document]) -> [Document]:

        if isinstance(documents, Document):
            documents = [documents]

        processedPile = []

        for doc in documents:

            # Process the document given knowledge in the extractor to form potential datapoints
            doc.processKnowledge(self)

            for point in doc.datapoints():
                point.prediction = self.ensemble[point.relation].predict(point)

            processedPile.append(doc)

        return processedPile

class RelationModel:
    """ The model the learns the sentence embeddings for a particular relationship """

    def fit(self, datapoints):

        # Cross validation in here
        pass

    def predict(self, point):
        return "yes"