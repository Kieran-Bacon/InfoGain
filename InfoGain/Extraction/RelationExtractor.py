from ..Documents import Datapoint, Document
from ..Knowledge import Ontology, Relation
from ..Resources.Models import Embedder

from .RelationModel import RelationModel

import os, sys

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
        
        # Data structure for traiing corpus
        self._trainingCorpus = set()

    def addRelation(self, relation: Relation):
        """ Add a new Relation to the extractor, overload the ontology's add relation. Adds to the 
        ensemble with a new relation model represent it 

        Params:
            relation (Relation) - The relation model to be added to the extractor
        """
        Ontology.addRelation(self, relation)  # Add the relation to the Extractor's ontology
        self.ensemble[relation.name] = RelationModel(relation)  # Generate a new relation model

    def fit(self, training_documents: [Document] ) -> None:
        """ Train the model on the collection of documents
        
        Params:
            training_documents (Document) - A collection of training files to fit the model on.
        """

        # Allow single or list of documents, convert training documents
        if isinstance(training_documents, Document):
            training_documents = [training_documents]

        for document in training_documents:

            # Record training document
            self._trainingCorpus.add(document)

            # Extract text representations and save them to the ontology
            [self.concept(name).alias.add(text) for name, textRepr in document.concepts().items() 
                for text in textRepr]

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

        for i, (model, data) in enumerate(modelData.items()):

            perc = i/(len(modelData))
            sys.stdout.write("\rTraining Extractor |" + "#"*int(perc*25) + "-"*(25-int(perc*25)) + 
                "| ( {}/{} ) training...".format(i, len(modelData)))
            sys.stdout.flush()

            self.ensemble[model].fit(data)

        sys.stdout.write("\rTraining Extractor |" + "#"*25 + 
            "| ( {}/{} ) training... Complete\n".format(len(modelData), len(modelData)))
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
            if not document.datapoints():
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

    def save(self, folder: str = "./", filename: str = "RelationExtractor") -> None:
        """ Save the Relation Extractor object along with the relevent supporting objects """

        import pickle
        with open(os.path.join(folder, filename), "wb") as handler:
            pickle.dump(self, handler, pickle.HIGHEST_PROTOCOL)