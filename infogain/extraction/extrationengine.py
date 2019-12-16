import os
import sys
import weakref
import collections
import re
from tqdm import tqdm
import itertools
import functools

from ..artefact import Document, Entity, Annotation
from ..knowledge import Concept, Relation
from ..knowledge.ontology import Ontology, OntologyConcepts, OntologyRelations

from .extractionrelation import ExtractionRelation
from .embedder import Embedder

import logging
log = logging.getLogger(__name__)

class ExtractionRelations(OntologyRelations):

    def __init__(self, owner: weakref.ref, relationClass = ExtractionRelation):
        self._ownerRef = owner
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

    def predict(self, document: Document) -> Document:
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
                for i, e in d1.entities.indexes(): document.entities.add(e, i)
                for ann in d1.annotations: document.annotations.add(ann)

        return document

    def score(self, documents: [Document], pprint: bool=False) -> (dict, dict):
        """ Calculate the precision, recall and F1 score for a collection of documents.
        The datapoints within the document are used to perform the scoring. The precision is
        calculated from the datapoints correctly returned in recall. A comparison is made between
        the annotation of the datapoint and its prediction.
        Recall is determined by processing the text of the datapoints using the ontology provided.
        The F1 score is an equation of the two other scores.

        Handles a single document or a collection

        Params:
            ontology (Ontology) - An ontology of concepts and relations to direct processing
            documents ([Document]) - A collection of document objects to score.
            print (bool) - A toggle to allow the output to be printed nicely to the screen

        Returns:
            corpus scores (dict) - A dictionary where the keys are the metrics, and the
                value is the collection averages
            document scores (dict) -  A dictionary where the keys are the documents, and
                the values are a dictionary of the metric values for that document
        """

        corpus = {
            'entities': {'precision': 0,  'recall': 0, 'f1': 0, 'sum': 0},
            'annotations': {'precision': 0,  'recall': 0, 'f1': 0, 'sum': 0}
        }
        scores = {}

        for document in documents:

            # Predict on the content to get new entities and annotations
            pred = self.predict(Document(document.content))

            # Calculate entity scores
            entityGroundTruth = set(i for i, _ in document.entities.indexes())
            entityPrediction = set(i for i, _ in pred.entities.indexes())
            overlap_indexes = entityGroundTruth.intersection(entityPrediction)

            entities_true_positive = sum(document.entities[i] == pred.entities[i] for i in overlap_indexes)
            entity_precision = entities_true_positive/len(pred.entities)
            entity_recall = entities_true_positive/len(document.entities)
            try:
                entity_f1 = (2*(entity_precision * entity_recall))/(entity_precision + entity_recall)
            except ZeroDivisionError:
                entity_f1 = 0

            # Calculate annotation scores
            document_annotations = tuple(ann for ann in document.annotations if ann.classification != Annotation.INSUFFICIENT)
            predict_annotations = tuple(ann for ann in pred.annotations if ann.classification != Annotation.INSUFFICIENT)

            annotation_true_positive = sum(
                predAnn == docAnn for predAnn in document_annotations for docAnn in predict_annotations
            )
            annotation_precision = annotation_true_positive/len([ann for ann in predict_annotations if ann.classification == Annotation.POSITIVE])
            annotation_recall = annotation_true_positive/len(document_annotations)
            try:
                annotation_f1 = (2*(annotation_precision * annotation_recall))/(annotation_precision + annotation_recall)
            except ZeroDivisionError:
                annotation_f1 = 0

            # Record the document scores
            scores[document] = {
                'entities': {'precision': entity_precision,  'recall': entity_recall, 'f1': entity_f1},
                'annotations': {'precision': annotation_precision,  'recall': annotation_recall, 'f1': annotation_f1}
            }

            corpus['entities']['sum'] += len(pred.entities)
            corpus['entities']['precision'] += entity_precision*len(pred.entities)
            corpus['entities']['recall'] += entity_recall*len(pred.entities)
            corpus['entities']['f1'] += entity_f1*len(pred.entities)

            corpus['annotations']['sum'] += len(pred.annotations)
            corpus['annotations']['precision'] = annotation_precision*len(pred.annotations)
            corpus['annotations']['recall'] = annotation_recall*len(pred.annotations)
            corpus['annotations']['f1'] = annotation_f1*len(pred.annotations)

        # Reduce the corpus data
        for value in corpus.values():
            for metric in ['precision', 'recall', 'f1']:
                value[metric] /= value['sum']

        if pprint:

            columns, widths = ['Artefact', 'Precision', 'Recall', 'F1'], [20]*4

            # define the row formats
            rowTemplate = '|'.join(['{'+str(i)+':^{'+str(i + len(columns))+'}}' for i in range(len(columns))])

            header = rowTemplate.format(*columns, *widths)
            print()
            print("{0:^{1}}".format('Entire corpus scores', len(header)))
            print('='*len(header))
            print(header)
            print('='*len(header))
            for k, v in corpus.items():
                print(rowTemplate.format(k, v['precision'], v['recall'], v['f1'], *widths))
            print()

            columns, widths = ['Document', 'Artefact', 'Precision', 'Recall', 'F1'], [max([len(doc.name) for doc in scores.keys()]) + 2] + [20]*4
            rowTemplate = '|'.join(['{'+str(i)+':^{'+str(i + len(columns))+'}}' for i in range(len(columns))])

            header = rowTemplate.format(*columns, *widths)
            print()
            print("{0:^{1}}".format('Document Scores', len(header)))
            print('='*len(header))
            print(header)
            print('='*len(header))

            for document, score in scores.items():
                # Print the scores for the document

                print(
                    rowTemplate.format(
                        document.name,
                        'entities',
                        score['entities']['precision'],
                        score['entities']['recall'],
                        score['entities']['f1'],
                        *widths
                    )
                )

                print(
                    rowTemplate.format(
                        '',
                        'annotations',
                        score['annotations']['precision'],
                        score['annotations']['recall'],
                        score['annotations']['f1'],
                        *widths
                    )
                )

                print('-'*len(header))

        print('\n\n')
        return corpus, scores