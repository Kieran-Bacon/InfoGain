from ..Documents import Datapoint, Document
from ..Knowledge import Ontology, Relation
from ..Resources.Models import Embedder

from .RelationModel import RelationModel

import os, sys, multiprocessing as mp
from multiprocessing.pool import Pool
from multiprocessing import Queue

import logging
log = logging.getLogger(__name__)

class RelationExtractor(Ontology):
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model.
    
    Params:
        name (str) - The name given to extractor
        filepath (str) - The path to an ontology file to load the extractor from
        ontology (Ontology) - An ontology object to be used to form the bases of the extraction
        word_embedding_model (Word2Vec) - An embedding model to be used other generating a new one
        min_count (int) - The minimum number of times a word needs to appear to be able to generate
            an embedding for.
        workers (int) - The number of threads/processors for the object
        alpha (float) - The alpha parameter to the Neural Network
        Hidden Layers (int,) - The network structure of the Neural Network classifiers
    """

    @classmethod
    def load(cls, filepath: str):
        """ Load a pickled relation extractor file 
        
        Params:
            filepath (str) - path to the pickled file
        
        Returns:
            RelationExtractor - A loaded pickled Relation Extractor object
        """
        import pickle
        with open(filepath, "rb") as handler:
            return pickle.load(handler)

    def __init__(self, name: str = None, 
        filepath: str = None,
        ontology: Ontology = None,
        word_embedding_model = None,
        embedding_size: int = 300,
        min_count: int = 10,
        workers: int = 4,
        alpha: float = None,
        hidden_layers: (int) = (50,20)):

        if filepath:
            # Call ontology constructor
            Ontology.__init__(self, name=name, filepath=filepath)

        elif ontology:
            # Convert ontology into a relation extractor instance
            ontologyClone = ontology.clone()
            self.name = ontologyClone.name if not ontologyClone is None else name
            self._concepts = ontologyClone._concepts
            self._relations = ontologyClone._relations

        self.embedder = Embedder(word_embedding_model, embedding_size, min_count, workers)
        
        # Record embedding information
        self.embeddingSize = self.embedder.size()
        self.MAXTHREADS = self.embedder.workers()

        # Inform the relation model of its static parameters
        RelationModel.setParameters(alpha, (self.embeddingSize, *hidden_layers))
    
        # Build relation model objects
        self.ensemble = {rel: RelationModel(rel) for rel in self.relations(keys=True)}

    def addRelation(self, relation: Relation):
        """ Add a new Relation to the extractor, overload the ontology's add relation. Adds to the 
        ensemble with a new relation model represent it 

        Params:
            relation (Relation) - The relation model to be added to the extractor
        """
        Ontology.addRelation(self, relation)  # Add the relation to the Extractor's ontology
        self.ensemble[relation.name] = RelationModel(relation)  # Generate a new relation model

    def fit(self, training_documents: [Document]) -> None:
        """ Train the model on the collection of documents
        
        Params:
            training_documents (Document) - A collection of training files to fit the model on.
        """

        # Allow single or list of documents, convert training documents
        if isinstance(training_documents, Document):
            training_documents = [training_documents]

        sentences = []
        for document in training_documents:
            
            # Store the text representations for the concept store
            [self.concept(name).alias.add(text)
                for name, textRepr in document.concepts().items()
                for text in textRepr]

            # Collect the words of the training documents 
            sentences += document.words(cleaned=True) # List of sentences, which are lists of words

        # Train embedder with training information
        self.embedder.train(sentences)

        # Separate out the datapoints for relation models specific collections
        modelData = {}
        for document in training_documents:
            for point in document.datapoints():
                # Pass the embedding function to the point to embed its context
                point.embedContext(self.embedder.sentence)
                # Store the embedded point
                modelData[point.relation] = modelData.get(point.relation, []) + [point]

        # Paremeters for multiprocessing
        poolsize = min(len(modelData), self.MAXTHREADS)
        trainingQueue, returnQueue = Queue(), Queue()

        # Add training data to training queue for processing
        [trainingQueue.put((self.ensemble[model], datapoints)) for model, datapoints in modelData.items()]

        # Start process pool
        processPool = Pool(poolsize, self._fit, (trainingQueue, returnQueue))

        # For each of the training models that have been scheduled, store fitted model
        for _ in range(len(modelData)):
            relationModel = returnQueue.get(True)
            if isinstance(relationModel, str): raise Exception("Error while fitting relation model")
            self.ensemble[relationModel.name] = relationModel

        processPool.close()

    @staticmethod
    def _fit(trainingQueue, returnQueue):
        """ Trains a single relation model, to be used as a multiprocess target function
        
        Params:
            trainingQueue (model, datapoints): A queue of the training material for the process to
                get work from
            returnQueue (mp.Queue): A queue for the training relation models to be put, to return
                them back to the main processes
        
        Returns:
            None - The function doesn't end. Process is to be killed when no more training documents
                in the training Queue.
        """

        while True:
            relationModel, datapoints = trainingQueue.get(True)  # Collect training data
            try:
                relationModel.fit(datapoints)  # train the model on the data
            except:
                log.error(
                    "Exception raised during fiting of relation model: {}".format(relationModel.name),
                    exc_info=True
                )
                returnQueue.put(relationModel.name)
                continue
            returnQueue.put(relationModel)  # return the training model
        
    def predict(self, documents: [Document]) -> [Document]:
        """
        Take a collection of documents and predict each of the extractable datapoints
        found. The documents are paralised to provide a performance boost. Documents have 
        datapoints classified and generated.

        Params:
            documents - A collection of Documents

        Returns:
            [Document] - Initial document collection (order altered) process and predicted
        """

        if isinstance(documents, Document):
            documents = [documents]

        poolsize = min(len(documents), self.MAXTHREADS)

        documentQueue, returnQueue = Queue(), Queue()
        [documentQueue.put(document) for document in documents]

        processPool = Pool(poolsize, self._predict, (self, documentQueue, returnQueue))

        predicted = []
        for _ in range(len(documents)):
            document = returnQueue.get(True)  # Get a predicted document
            if isinstance(document, str): raise Exception("Error while processing document: {}".format(document))
            predicted.append(document)

        processPool.close()

        return predicted

    @staticmethod
    def _predict(extractor, documentQueue, returnQueue):
        """ Processed a document according to the extractor, predict the datapoints of the 
        documents and return the processed documents. To be run as a multiprocessing process
        taking an extractor and a queues for the pick up and drop off of documents.
        
        Params:
            extractor (RelationExtractor): The extractor trained to predict the datapoints
            documentQueue (mp.Queue): Queue of documents to be processed - work picked up here
            returnQueue (mp.Queue): Queue where processed documents are placed
            
        Returns:
            None - The function doesn't end. To be killed after documents have all been predicted
        """

        while True:
            document = documentQueue.get(True)  # Get the document

            # Produce datapoints for the document if not already produced
            if not len(document.datapoints()): document.processKnowledge(extractor)

            # Seperate the points while embedding them
            predictData = {}
            for point in document.datapoints():
                point.embedContext(extractor.embedder.sentence)
                predictData[point.relation] = predictData.get(point.relation, []) + [point]

            # Predict the points
            predictedPoints = []
            for relation, points in predictData.items():
                predictedPoints += extractor.ensemble[relation].predict(points)

            # Pass predicted points back to the document
            document.datapoints(predictedPoints)
            returnQueue.put(document)  # Return the document

    def save(self, folder: str = "./", filename: str = "RelationExtractor") -> None:
        """ Save the Relation Extractor object along with the relevent supporting objects """

        import pickle
        with open(os.path.join(folder, filename), "wb") as handler:
            pickle.dump(self, handler, pickle.HIGHEST_PROTOCOL)