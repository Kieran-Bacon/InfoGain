from .Embedder import Embedder
from .RelationModel import RelationModel

from ..Knowledge import Ontology
from ..Documents import Datapoint, Document
from .. import Resources

import os, numpy, logging, sys

from queue import Queue
from threading import Thread

class UnseenWord(Exception):
    pass

class RelationExtractor(Ontology):
    """ This object represents a machine learning method of extracting relationships
    from provided corpora. The object maintains a collection of classifiers
    which in turn provide evidence for various relationships. The class provides 
    a collection of useful methods for interacting with the model. """

    def __init__(self, name: str = None, 
        filepath: str = None,
        ontology: Ontology = None,
        word_embedding_model = None,
        embedding_size: int = 300,
        min_count: int = 10,
        workers: int = 4,
        alpha: float = None,
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

        self.embedder = Embedder(word_embedding_model, embedding_size, min_count, workers)
        
        # Record embedding information
        self.embeddingSize = self.embedder.size()
        self.MAXTHREADS = self.embedder.workers()

        # Inform the relation model of its static parameters
        RelationModel.setParameters(alpha, (self.embeddingSize, *hidden_layers))
    
        # Build relation model objects
        self.ensemble = {rel: RelationModel(rel) for rel in self.relations(keys=True)}
        
        # Data structure for traiing corpus
        self._trainingCorpus = set()

    def fit(self, training_documents: [Document] ) -> None:
        """ Use the provided annotated document to provide training data to the
        regressors of
        
        Params:
            - annotations: A single file, or a list of file paths to training documents
        """

        # Allow single or list of documents, convert training documents
        if isinstance(training_documents, Document):
            training_documents = [training_documents]

        for document in training_documents:

            # Record training document
            self._trainingCorpus.add(document)

            # Extract text representations and save them to the ontology
            [self.concept(name).alias.add(text) for name, textRepr in document.concepts().items() for text in textRepr]

        # Collect sentences from training documents - Train word embedder on sentences
        sentences = []
        for document in self._trainingCorpus:
            sentences += document.words(cleaned=True)
        self.embedder.train(sentences)

        # Separate out the datapoints for relation models specific collections
        modelData = {rel: [] for rel in self.ensemble.keys()}
        for document in training_documents:
            for point in document.datapoints():
                # Pass the embedding function to the point to embed its context
                point.embedContext(self.embedder.sentence)
                # Store the embedded point
                modelData[point.relation].append(point)

        self._trainModels(modelData)

    def _trainModels(self, model_datapoints: {str:[Datapoint]}) -> None:

        """

        start = time.time()

        def trainRelationModel(queue: Queue):
            while True:
                data = queue.get()
                if data is None: break

                rel, data = data  # Expand the struction
                self.ensemble[rel].fit(data)  # Fit the data
                queue.task_done()  # Single that the task is done

        relationQueue = Queue()

        num_threads = range(min(len(model_datapoints), self.MAXTHREADS))
        threads = [Thread(target=trainRelationModel, args=(relationQueue,)) for _ in num_threads]

        # Start threads and add relations data to processing queue
        [t.start() for t in threads]
        [relationQueue.put(data) for data in model_datapoints.items()]

        size = 0
        while relationQueue.unfinished_tasks:
            if relationQueue.unfinished_tasks == size: continue
            else: size = relationQueue.unfinished_tasks
            count = len(model_datapoints) - relationQueue.unfinished_tasks
            mult = 25 - int((relationQueue.unfinished_tasks/len(model_datapoints)*25))
            sys.stdout.write("\rTraining Extractor |" + "#"*mult + "-"*(25-mult) + "| ( {}/{} ) training...".format(count, len(model_datapoints) ))
            sys.stdout.flush()

        # Process till training is complete
        relationQueue.join()
        
        # Pretty prompt
        sys.stdout.write("\rTraining Extractor |" + "#"*25 + "| ( {}/{} ) training... Complete!\n".format(len(model_datapoints),len(model_datapoints)))
        sys.stdout.flush()

        # Signal the threads to stop computation and join
        [relationQueue.put(None) for _ in num_threads]
        [t.join() for t in threads]

        print(time.time()-start)

        return"""

        for i, (model, data) in enumerate(model_datapoints.items()):

            perc = i/(len(model_datapoints))
            sys.stdout.write("\rTraining Extractor |" + "#"*int(perc*25) + "-"*(25-int(perc*25)) + "| ( {}/{} ) training...".format(i, len(model_datapoints)))
            sys.stdout.flush()

            self.ensemble[model].fit(data)

        sys.stdout.write("\rTraining Extractor |" + "#"*25 + "| ( {}/{} ) training... Complete\n".format(len(model_datapoints), len(model_datapoints)))
        sys.stdout.flush()
        
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

        for document in documents:
            
            # Process the knowledge
            document.processKnowledge(self)

            # Extract the datapoints from the document
            
            models = {rel: [] for rel in self.ensemble.keys()}
            for point in document.datapoints():
                point.embedContext(self.embedder.sentence)
                models[point.relation].append(point)

            predicted = []
            for rel, datapoints in models.items():
                predicted += self.ensemble[rel].predict(datapoints)

            document.datapoints(predicted)

        return documents