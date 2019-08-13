import os
import sys
import weakref
import collections
import re
from tqdm import tqdm

from ..artefact import Datapoint, Document
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

    def fit(self, documents: [Document]):
        """ Train the model on the collection of documents (InfoGain documents)

        Params:
            documents ([Document]) - A collection of training files to fit the model on.
        """

        if not isinstance(documents, collections.abc.Iterable): documents = [documents]

        relation_datapoints = collections.defaultdict(list)
        for document in documents:

            for datapoint in document.datapoints():

                # Train the entity detection with the datapoint entities
                for entity in (datapoint.domain, datapoint.target):
                    concept = self.concepts.get(entity)
                    if concept is not None:
                        concept.aliases.add(entity.text)

                # Split out the datapoints for training relations
                relation = self.relations.get(datapoint.relation)
                if relation:
                    relation_datapoints[relation].append(datapoint)

            # Train the embedder
            self.embedder.train(document.words(cleaned=True))

        for relation, datapoints in relation_datapoints.items():
            relation.fit(datapoints)

    def predict(self, document: Document):
        """ Identify entities and relationships within the document and predict their confidences

        Parmas:
            document (Document): The document to be predicted on
        """

        # A store mapping aliases to concepts
        aliases = collections.defaultdict(set)
        for concept in self.concepts:
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
                    represention_1, matchObj_1, concept_1 = scenarioEntities.pop()

                    # Comparing with remaining entities
                    for represention_2, matchObj_2, concept_2 in scenarioEntities:

                        # Determine sentence context - due to finder iter and pop, obj 1 always behind obj 2
                        context = {
                            "left": sentence[:matchObj_2.span()[0]],
                            "middle": sentence[matchObj_2.span()[1]: matchObj_1.span()[0]],
                            "right": sentence[matchObj_2.span()[1]:],
                        }
                        embeddings = {
                            key: self.embedder.sentence(Document.clean(value))
                            for key, value in context
                        }

                        wrapper_1, wrapper_2 = (con_1, matchObj_1), (con_2, matchObj_2)

                        # The entities can be in either order for relations - look at both orientations
                        for dc, dm, tc, tm in [(wrapper_1, wrapper_2), (wrapper_2, wrapper_1)]:

                            # Create a datapoint for each relationship found
                            for relation in self.findRelations(dc, tc):
                                point = Datapoint({
                                    "domain": {"concept": dc, "text": dm.group(0).strip()},
                                    "target": {"concept": tarCon, "text": tm.group(0).strip()},
                                    "relation": relation.name,
                                    "text": sentence,
                                    "context": context,
                                    "embedding": embeddings
                                })

                                self.relations[relation].predict(point)

                                scenarioDatapoints.append(point)


                # Add the Scenario datapoints into the sentence data point container for comparison
                datapoints.append(scenarioDatapoints)

            # Compare the different scenarios
            if datapoints:

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