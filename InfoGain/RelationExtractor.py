from .Ontology import Ontology

from .Documents.Document import Document
from .Documents.TrainingDocument import TrainingDocument

import InfoGain.Resources as RESOURCES
import InfoGain.Resources.TextCollections as TEXT
import InfoGain.Documents.DocumentOperations as DO

import os, numpy, logging, sys
from queue import Queue
from threading import Thread

from sklearn.neural_network import MLPClassifier
from gensim.models import Word2Vec

class UnseenWord(Exception):
    pass

class RelationExtractor(Ontology):
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self,
        name: str = None,
        filepath: str = None,
        ontology: Ontology = None,
        word_embedding_model: Word2Vec = None,
        embedding_size: int = 300,
        min_count: int = 1,
        workers: int = 4,
        hidden_layers: (int) = (50,20)):
        """ Initialising the pool of relation classifiers and defining the method of learning
        that will take place.

        Params:
            ont - The ontology that defines the relationships of interest that can
                show up inside the text
            k - The number of words taken as context from either side of the 
                relation entities
        """

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

        # Overload name if given
        if name: self.name = name

        # Load resouces embedder if embedder not provided
        if word_embedding_model is None and RESOURCES.hasEmbedder():
            word_embedding_model = RESOURCES.loadEmbedder()

        # Collect information from embedder or generate new embedder
        if word_embedding_model:
            self.wordModel = word_embedding_model
        else:
            # Define the word model
            self.wordModel = Word2Vec(size=embedding_size, min_count=min_count, workers=workers)

            # Collect the text data
            documents = [Document(filepath=path) for path in RESOURCES.TEXT_COLLECTIONS]
            sentences = [DO.cleanSentence(sentence).split() for doc in documents for sentence in doc.sentences()]
            
            
            # Help build spelling Corrector
            self.wordModel.build_vocab(sentences)

        # Record embedding information
        self.embeddingSize = self.wordModel.layer1_size
        self.MAXTHREADS = self.wordModel.workers

        # Inform the relation model structure
        RelationModel.defineStructure((self.embeddingSize, *hidden_layers))
    
        # Build relation model objects
        self.ensemble = {rel.name:RelationModel(rel.name) for rel in self.relations()}
        
        # Data structure for traiing corpus
        self._trainingCorpus = set()

    def _trainWordEmbeddings(self):
        """ Train the word embedding model on the words provided by the training documents """

        # Collect sentences from training documents
        sentences = [DO.cleanSentence(sentence).split() for doc in self._trainingCorpus for sentence in doc.sentences()]

        self.wordModel.build_vocab(sentences, update=True)
        self.wordModel.train(sentences, total_examples=len(sentences), epochs=1)

    def _embedSentence(self, sentence: str) -> numpy.array:
        """ Convert a sentence of variable length into a sentence embedding using the learn word
        embeddings"""

        embedding = numpy.zeros(self.embeddingSize)
        words = sentence.split()

        def pf(index: int) -> float:
            """ Return the output of a monotonic function as to reduce traling word embeddings """
            # TODO: Change function to something meaningful with support from someone
            return 1  #-numpy.log((index+1)/(len(words)+1))

        for index, word in enumerate(words):
            if not word in self.wordModel.wv:
                logging.warning("Vocabulary missing during sentence embedding: '"+ word +"'")
                continue
            embedding += pf(index)*self.wordModel.wv[word]
                
        return embedding if not len(words) else embedding/len(words)

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
                modelData[point.relation].append(point)

        # Begin training of the relation models, threading each model for efficiency
        def trainRelationModel(queue: Queue):
            while True:
                data = queue.get()
                if data is None: break

                rel, data = data  # Expand the struction
                self.ensemble[rel].fit(data)  # Fit the data
                queue.task_done()  # Single that the task is done

        # Begin the relation queue structure
        relationQueue = Queue()

        num_threads = range(min(len(modelData), self.MAXTHREADS))
        threads = [Thread(target=trainRelationModel, args=(relationQueue,)) for _ in num_threads]

        # Start threads and add relations data to processing queue
        [t.start() for t in threads]
        [relationQueue.put(data) for data in modelData.items()]

        size = 0
        while relationQueue.unfinished_tasks:
            if relationQueue.unfinished_tasks == size: continue
            else: size = relationQueue.unfinished_tasks
            count = len(modelData) - relationQueue.unfinished_tasks
            mult = 25 - int((relationQueue.unfinished_tasks/len(modelData)*25))
            sys.stdout.write("\rTraining Extractor |" + "#"*mult + "-"*(25-mult) + "| ( {}/{} ) training...".format(count, len(modelData) ))
            sys.stdout.flush()

        # Process till training is complete
        relationQueue.join()
        
        # Pretty prompt
        sys.stdout.write("\rTraining Extractor |" + "#"*25 + "| ( {}/{} ) training... Complete!\n".format(len(modelData),len(modelData)))
        sys.stdout.flush()

        # Signal the threads to stop computation and join
        [relationQueue.put(None) for _ in num_threads]
        [t.join() for t in threads]
        
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

        # Set up document queue and processed pile
        documentQueue, processedPile = Queue(), set()

        # Generate threads
        num_threads = range(min(len(documents), self.MAXTHREADS))
        threads = [Thread(target=self._predictDocument, args=(documentQueue, processedPile)) for _ in num_threads]

        # Start threads and add documents to processing queue
        [t.start() for t in threads]
        [documentQueue.put(document) for document in documents]

        # Process till documents are complete
        documentQueue.join()

        # Signal the threads to stop computation and join
        [documentQueue.put(None) for _ in num_threads]
        [t.join() for t in threads]

        return list(processedPile)

    def _predictDocument(self, documentQueue: Queue, processedPile: set):

        while True:
            document = documentQueue.get()
            if document is None: break  # No more documents to process

            # Process the document according to the ontology
            document.processKnowledge(self)

            # Extract the datapoints from the document
            documentPredictions = []
            for segment in document.datapoints():

                # Separate out the datapoints into relations
                models = {}
                for point in segment:
                    # Pass the embedding function to convert its context
                    point.embedContext(self._embedSentence)
                    collection = models.get(point.relation, [])
                    collection.append(point)
                    models[point.relation] = collection

                # Predict the points by their respective models
                predictedPoints = []
                for model, collection in models.items():
                    # Predict on the datapoints
                    predictions = self.ensemble[model].predict(collection)
                    if predictions is None: continue  # Protect against unfitted models

                    # Record predictions
                    predictedPoints += predictions

                # Store the points and their predictions
                documentPredictions.append(predictedPoints)

            # Return to the document the new point set
            document.datapoints(documentPredictions)

            # Add document to the processed pile and complete task
            processedPile.add(document)
            documentQueue.task_done()
                
class RelationModel:
    """ The model the learns the sentence embeddings for a particular relationship """

    structure = (900, 5)
    #structure = (900,50,20)

    @classmethod
    def defineStructure(cls, shape: tuple):
        cls.structure = shape

    def __init__(self, name: str):
        self.name = name
        self.classifier = MLPClassifier(hidden_layer_sizes=RelationModel.structure)
        self.fitted = False

    def fit(self, datapoints):
        """ Fit the datapoints """

        # Do nothing if no datapoints have been provided
        if not len(datapoints):
            logging.warning("Fitting Relation model for '"+self.name+"' without any datapoints")
            return 

        # Convert the point structure into something usable by sklearn

        Xtr, ttr = [], []
        for point in datapoints:
            x, t = point.features()
            Xtr.append(numpy.concatenate(x))
            ttr.append(t)
            
        # Fit the classifier
        self.classifier.fit(Xtr, ttr)
        self.fitted = True

        # TODO: Cross Validation


    def predict(self, points):

        if not self.fitted:
            logging.error("Attempt to predict on unfitted relation model: " + self.name)
            return

        # Extract data point feature information
        Xte = []
        for point in points:
            x, _ = point.features()
            Xte.append(numpy.concatenate(x))

        # Predict on the data
        predictions = self.classifier.predict(Xte)
        probabilities = self.classifier.predict_proba(Xte)

        for point, pred, prob in zip(points, predictions, probabilities):
            assert(pred == int(pred))
            point.prediction = int(pred)
            point.predProb = float(prob[list(self.classifier.classes_).index(pred)])

        processedPoints = []

        # Verify the points
        while points:

            # Extract each point
            point = points.pop()

            # Find any duplicate relations
            duplicates = [p for p in points if point.isDuplicate(p)]

            # Extract them and remove them from the orginal structure
            for p in duplicates:
                del points[points.index(p)]

            while duplicates:

                # Iteratively record out of the duplicated points the one with the greatest probability
                dup = duplicates.pop()
                point = point if point.predProb > dup else dup

            # Store the winner
            processedPoints.append(point)

        return processedPoints
            
