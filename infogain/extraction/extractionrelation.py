import numpy as np
from sklearn.neural_network import MLPClassifier

from ..artefact import Annotation
from ..knowledge import Relation

import logging
log = logging.getLogger(__name__)

class ExtractionRelation(Relation):

    def __init__(self, *args, **kwargs):
        self.classifier = MLPClassifier(hidden_layer_sizes=(900, 50, 20))
        self.fitted = False
        super().__init__(*args, **kwargs)

    def fit(self, annotations: [Annotation]) -> None:
        """ Use the datapoints to train the relation model

        Params:
            datapoints (Annotation) - A collection of datapoints for this relation to train on
        """

        # Do nothing if no datapoints have been provided
        if not len(annotations):
            raise RuntimeError("Called fit on model with no training data for '{}' relation".format(self.name))

        # Convert the point structure usable by sklearn
        Xtr, ttr = [], []
        for ann in annotations:
            Xtr.append(np.concatenate(ann.embedding))
            ttr.append(ann.annotation)

        # Fit the classifier
        self.classifier.fit(Xtr, ttr)
        self.fitted = True

    def predict(self, point: Annotation) -> Annotation:
        """ Use the relation model to predict on a collection of points and return the points

        Params:
            points (Annotation) - A collection of datapoints to be predicted on
        """

        if not self.fitted:
            raise RuntimeError("attempted to run predict with '{}' relation before being trained".format(self.name))

        # Predict the point with the relation's classifier
        probs = self.classifier.predict_proba([np.concatenate(point.embedding)])[0]

        # Convert probability vector into the class and associated probability of the most likely class
        point.classification, point.probability = max(zip(self.classifier.classes_, probs), key = lambda x: x[1])
        return point

    @classmethod
    def fromRelation(self, relation: Relation):
        return ExtractionRelation(
            relation.domains,
            relation.name,
            relation.targets,
            rules = [rule for rule in relation.rules],
            differ = relation.differ
        )