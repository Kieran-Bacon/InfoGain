import sys, os, better
from tqdm import tqdm

from ..artefact import Datapoint, Document
from ..knowledge import Ontology, Relation

from .relationmodel import RelationModel
from .embedder import Embedder

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
        workers: int = os.cpu_count(),
        alpha: float = None,
        hidden_layers: (int) = (50,20)):

        if filepath:
            # Call ontology constructor
            Ontology.__init__(self, name=name, filepath=filepath)

        elif ontology:
            # Convert ontology into a relation extractor instance
            Ontology.__init__(self)
            ontologyClone = ontology.clone()
            self.name = ontologyClone.name if not ontologyClone is None else name
            self._concepts = ontologyClone._concepts
            self._relations = ontologyClone._relations

        self.embedder = Embedder(word_embedding_model, embedding_size, min_count, workers)

        # Record embedding information
        self.embeddingSize = self.embedder.size()
        self.MAXTHREADS = workers

        # Inform the relation model of its static parameters
        RelationModel.setParameters(alpha, (self.embeddingSize, *hidden_layers))

        # Build relation model objects
        self.ensemble = {rel: RelationModel(rel) for rel in self.relations(names=True)}

    def addRelation(self, relation: Relation):
        """ Add a new Relation to the extractor, overload the ontology's add relation. Adds to the
        ensemble with a new relation model represent it

        Params:
            relation (Relation) - The relation model to be added to the extractor
        """
        Ontology.addRelation(self, relation)  # Add the relation to the Extractor's ontology
        self.ensemble[relation.name] = RelationModel(relation.name)  # Generate a new relation model

    def fit(self, training_documents: [Document]) -> None:
        """ Train the model on the collection of documents

        Params:
            training_documents (Document) - A collection of training files to fit the model on.
        """

        log.debug("Fitting the relation extractor - {} training documents".format(len(training_documents)))

        # Allow single or list of documents, convert training documents
        if isinstance(training_documents, Document): training_documents = [training_documents]

        # Process the documents and train the embedder - set up the process for working on the documents
        relation_counter = {}
        for document in training_documents:

            # Store the text representations for the concept store
            for concept_name, text_repr in document.concepts().items():
                concept = self.concepts(concept_name)
                concept.alias = concept.alias.union(text_repr)

            # Collect the number of relations within set
            for relation_name, counter in document.relations().items():
                relation_counter[relation_name] = relation_counter.get(relation_name, 0) + counter

            # Train the embedder
            self.embedder.train(document.words(cleaned=True))

        relations_to_process = sorted(relation_counter.keys(), key = lambda x: relation_counter[x])

        # Set up containers for document datapoints after processing
        models_training_containter = {
            name: {
                "document": Document("{} training set".format(name)),
                "lock": better.threading.Lock()
            }
            for name in relations_to_process
        }

        def processing_document(document: Document):
            """ Process a document and separate out the contents into the correct relation documents

            Params:
                document: A document object containing some datatpoints
            """
            for point in document.datapoints():
                point.embedContext(self.embedder.sentence)  # Embed the point so that it can be used to train the model

                # Place into the relation training document
                with models_training_containter[point.relation]["lock"]:
                    models_training_containter[point.relation]["document"].addDatapoint(point)
        better.threading.tfor(processing_document, training_documents)

        with better.multiprocessing.PoolManager(self._fit) as pool:

            for relation in relations_to_process:
                pool.put(self.ensemble[relation], models_training_containter[relation]["document"])

            for _ in range(len(relations_to_process)):
                model = pool.get()
                self.ensemble[model.name] = model

    @staticmethod
    def _fit(relation_model: RelationModel, training_document: Document) -> RelationModel:
        """ Taking a RelationModel, and a training document that contains only datapoints for that model. Train the
        model with the datapoints and return the newly training RelationModel

        Params:
            relation_model (RelationModel): The relation model to train
            training_document (Document): The document to train the model from, containing datapoints for one relation
        """
        relation_model.fit(training_document.datapoints())
        return relation_model

    def predict(self, documents: [Document]) -> [Document]:
        """ Take a collection of documents and predict each of the extractable datapoints
        found. The documents are paralised to provide a performance boost. Documents have
        datapoints classified and generated.

        Params:
            documents - A collection of Documents

        Returns:
            [Document] - Initial document collection (order altered) process and predicted
        """
        # Set up the environment such that a process exists for a particular relation
        if isinstance(documents, Document): return self._predict(documents, self)

        predicted_documents = []
        with better.multiprocessing.PoolManager(self._predict, static_args=[self], ordered=True) as pool:
            pool.put_async(documents)
            for _ in tqdm(range(len(documents)), ascii=True, desc="Documents Predicted"):
                predicted_documents.append(pool.get())  # Get the documents back

        return predicted_documents

    @staticmethod
    def _predict(document: Document, extractor) -> Document:
        """ Processed a document according to the extractor, predict the datapoints of the
        documents and return the processed documents. To be run within a multiprocessing environment.

        Params:
            document (Document): The document to be predicted
            extractor (RelationExtractor): The extractor model that is to predict the document

        Returns:
            Document: A document of the same type as the initial document, containing predicted datapoints
        """
        # Generate document datapoints according to the extractor, if the document doesn't have any datapoints
        if not document.hasDatapoints(): document.processKnowledge(extractor)

        # Create a new document to store predicted datapoints and to be returned
        predicted_document = document.clone(meta_only=True)
        for point in document.datapoints():
            point.embedContext(extractor.embedder.sentence)
            predicted_point = extractor.ensemble[point.relation].predict([point])[0]
            predicted_document.addDatapoint(predicted_point)

        return predicted_document

    def save(self, folder: str = "./", filename: str = "RelationExtractor") -> None:
        """ Save the Relation Extractor object along with the relevent supporting objects """

        import pickle
        with open(os.path.join(folder, filename), "wb") as handler:
            pickle.dump(self, handler, pickle.HIGHEST_PROTOCOL)