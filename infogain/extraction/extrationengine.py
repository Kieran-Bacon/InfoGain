import os
import sys
import weakref
import collections
import re
from tqdm import tqdm
import itertools

from ..artefact import Document, Entity, Annotation
from ..knowledge import Concept, Relation
from ..knowledge.ontology import Ontology, OntologyConcepts, OntologyRelations

from .extractionrelation import ExtractionRelation
from .embedder import Embedder

import logging
log = logging.getLogger(__name__)

class ExtractionRelations(OntologyRelations):

    def __init__(self, owner: weakref.ref, relationClass = ExtractionRelation):
        self._owner = owner
        self._relationClass = relationClass
        self._elements = {}

    def add(self, relation: Relation) -> Relation:
        if isinstance(relation, Relation): relation = self._relationClass.fromRelation(relation)
        return super().add(relation)

class ExtractionEngine(Ontology):
    """ TODO

    Params:
        name (str) - The name given to extractor
        ontology (Ontology) - An ontology object to be used to form the bases of the extraction
        *,
        embedder (Embedder): Object that shall embed words and sentences into the apprioprate vectors for the models
        relation_class (ExtractionRelation): A Relation class implementing a method for predicting on embeddings
    """

    def __init__(
        self,
        name: str = None,
        ontology: Ontology = None,
        *,
        embedder: Embedder = Embedder(),
        relation_class = ExtractionRelation
    ):
        self.name = name

        self._concepts = OntologyConcepts(weakref.ref(self))
        self._relations = ExtractionRelations(weakref.ref(self), relation_class)

        self._embedder = embedder

        if ontology:
            # Add each of the items of the provided ontology into the engine - clone elements to avoid coupling issues
            if self.name is None and ontology.name is not None:
                self.name = ontology.name

            for concept in ontology.concepts():
                self.concepts.add(concept.clone())

            for relation in ontology.relations():
                self.relations.add(relation.clone())

    def fit(self, documents: [Document]):
        """ Train the model on the collection of documents (InfoGain documents)

        Params:
            documents ([Document]) - A collection of training files to fit the model on.
        """

        if isinstance(documents, Document): documents = [documents]

        relation_datapoints = collections.defaultdict(list)
        for document in documents:

            for annotation in document.annotations:

                # Train the entity detection with the datapoint entities
                for entity in (annotation.domain, annotation.target):
                    concept = self.concepts.get(entity.classType)
                    if concept is not None:
                        concept.aliases.add(entity.surfaceForm)

                # Split out the datapoints for training relations
                relation = self.relations.get(annotation.name)
                if relation:
                    relation_datapoints[relation].append(annotation)

            # Train the embedder - only take alpha words
            self._embedder.train([[word for word in sentence if word.isalpha()] for sentence in document.sentences()])
            # self._embedder.train(word for word in document.words() if word.isalpha())

        # Embed the annotations and train their relations
        for relation, annotations in relation_datapoints.items():
            for ann in annotations: ann.embedding = tuple(self._embedder.sentence(context) for context in ann.context)
            relation.fit(annotations)

    def oldpredict(self, document: Document):
        """ Identify entities and relationships within the document and predict their confidences

        Parmas:
            document (Document): The document to be predicted on
        """

        # A store mapping aliases to concepts
        aliases = collections.defaultdict(set)
        for concept in self.concepts():
            if concept.category is Concept.ABSTRACT: continue

            aliases[concept.name].add(concept.name)
            for alias in concept.aliases:
                aliases[alias].add(concept.name)

        #? This can become the fast text algorithm
        # Identify the text within the documents
        patterns = [
            (
                pattern,
                re.compile(r"(^|(?!\s))"+pattern+r"((?=(\W(\W|$)))|(?=\s)|(?='s)|$)")
            )
            for pattern in aliases.keys()
        ]

        # For each sentence of the document predict datapoints
        for sentence in document.sentences():

            # Find all the specified entities within the text
            entities = [(rep, match) for rep, pattern in patterns for match in pattern.finditer(sentence)]
            #! Implement the NER method here for entities
            #// entities += self._predictNRE(sentence)

            datapoints = []
            for scenario in itertools.product(*[aliases[entity[0]] for entity in entities]):

                # Combine the scenario concept with the concept
                scenarioEntities = []
                for i in range(len(entities)):
                    scenarioEntities.append((*entities[i], scenario[i]))

                # Container for datapoints made with this base assumption
                scenarioDatapoints = []

                while scenarioEntities:
                    # Remove an entity to compare with others - reduce the entities list
                    _, matchObj_1, concept_1 = scenarioEntities.pop()

                    # Comparing with remaining entities
                    for _, matchObj_2, concept_2 in scenarioEntities:

                        # Determine sentence context - due to finder iter and pop, obj 1 always behind obj 2
                        context = {
                            "left": sentence[:matchObj_2.span()[0]],
                            "middle": sentence[matchObj_2.span()[1]: matchObj_1.span()[0]],
                            "right": sentence[matchObj_2.span()[1]:],
                        }
                        embeddings = {
                            key: self._embedder.sentence(Document.clean(value))
                            for key, value in context.items()
                        }

                        wrapper_1, wrapper_2 = (concept_1, matchObj_1), (concept_2, matchObj_2)

                        # The entities can be in either order for relations - look at both orientations
                        for (dc, dm), (tc, tm) in [(wrapper_1, wrapper_2), (wrapper_2, wrapper_1)]:

                            # Create a datapoint for each relationship found
                            for relation in self.findRelations(dc, tc):
                                point = Datapoint({
                                    "domain": {"concept": dc, "text": dm.group(0).strip()},
                                    "target": {"concept": tc, "text": tm.group(0).strip()},
                                    "relation": relation.name,
                                    "text": sentence,
                                    "context": context,
                                    "embedding": embeddings
                                })

                                relation.predict(point)

                                scenarioDatapoints.append(point)


                # Add the Scenario datapoints into the sentence data point container for comparison
                datapoints.append(scenarioDatapoints)

            # Compare the different scenarios
            if any(len(points) for points in datapoints):

                # Ensure that all scenarios have some datapoints - order them by probability for comparison
                datapoints = [
                    sorted(scenario, key=lambda e: e.probability, reverse=True)
                    for scenario in datapoints if len(scenario) > 0
                ]

                # Select a scenario - doesn't matter what one
                selected = datapoints.pop()

                while datapoints:
                    comparison = datapoints.pop()

                    length = min(len(selected), len(comparison))

                    si, ss, ci, cs = 0, 0, 0, 0
                    for i in range(length):
                        if selected[si] > comparison[si]:
                            ss += i
                            si += 1
                        else:
                            cs += i
                            ci += 1

                    # Replace the selected datapoints with the comparison set
                    if ss > cs:
                        selected = comparison

                # A selected Scenario has been chosen - add it to the document
                for datapoint in selected:
                    document.addDatapoint(datapoint)

        return document

    def predict(self, document: Document):
        """ Identify entities and relationships within the document and predict their confidences

        Parmas:
            document (Document): The document to be predicted on
        """

        # A store mapping aliases to concepts
        aliases = collections.defaultdict(set)
        for concept in self.concepts():
            if concept.category is Concept.ABSTRACT: continue

            aliases[concept.name].add(concept.name)
            for alias in concept.aliases:
                aliases[alias].add(concept.name)

        #? This can become the fast text algorithm
        # Identify the text within the documents
        patterns = [
            (
                pattern,
                re.compile(r"(^|(?!\s))"+pattern+r"((?=(\W(\W|$)))|(?=\s)|(?='s)|$)")
            )
            for pattern in aliases.keys()
        ]

        print("Finished setting up the aliases")

        # For each sentence of the document predict datapoints
        for sentence in document.sentences():
            print("Yielding sentences: "+sentence)

            # Find all entities within the sentence - stack them upon their spans so patterns matching for the same
            entities = collections.defaultdict(set)
            for (rep, pattern) in patterns:
                for match in pattern.finditer(sentence):

                    # Found a possible entity - convert the pattern used into possible entities for the match
                    for concept in aliases[rep]:
                        entities[match.span()].add(Entity(concept, match.group(0)))

            # Check to see if any information was identified
            if not entities: continue

            # Collapse the structure into two lists, the span list and a list of sets of representations
            spans, ents = zip(*entities.items())

            # Choose for the conflicts a single scenario for their occurrence
            scenarioDocuments = []
            for scenario in itertools.product(*ents):

                # Create a document to represent this sentence and this entity setup
                sceneDocument = Document(sentence, processed=True)

                # Add the entities to the document
                for span, entity in zip(spans, scenario): sceneDocument.entities.add(entity, span[0])

                # Loop over scenario entities to find possible annotations to be made
                scenario = list(scenario)
                while scenario:
                    # Extract an entity
                    e1 = scenario.pop()

                    # Loop over the remaining entities
                    for e2 in scenario:

                        # Investigate relations that can form in either direction
                        for first, second in [(e1, e2), (e2, e1)]:

                            # For any valid relationships that can be formed between the entities
                            for relation in self.findRelations(first.classType, second.classType):

                                # Create an annotation object and add it to the document for context and validation
                                ann = Annotation(first, relation.name, second)
                                sceneDocument.annotations.add(ann)

                                # Embed the annotation and predict it
                                ann.embedding = tuple(self._embedder.sentence(context) for context in ann.context)
                                relation.predict(ann)

                scenarioDocuments.append(sceneDocument)

            # Compare the different scenarios
            if any(len(sceneDocument.annotations) for sceneDocument in scenarioDocuments):

                order = lambda doc: sorted(doc.annotations, key = lambda ann: ann.probability, reverse=True)

                # Extract a starting document
                d1 = scenarioDocuments.pop()
                ann1 = order(d1)

                while scenarioDocuments:

                    # Extract a comparison document
                    d2 = scenarioDocuments.pop()
                    ann2 = order(d2)

                    # Compete for value of the scenario
                    counter, si, ci = 0, 0, 0
                    length = min(len(ann1), len(ann2))
                    for i in range(length):
                        if ann1[si].probability < ann2[ci].probability:
                            counter += (length - i)**2
                            ci += 1
                        else:
                            counter -= (length - i)**2
                            si += 1

                    # Choose the document with the greatest relative confidences
                    if counter >= 0:
                        d1, ann1 = d2, ann2

                # Add the document information and its entities/annotations
                import time
                print("Before inputing entities")
                for i, e in d1.entities.indexes():
                    print("Entity: {} {}".format(i, e))
                    document.entities.add(e, i)
                    time.sleep(1)
                for ann in d1.annotations: document.annotations.add(ann)

        return document