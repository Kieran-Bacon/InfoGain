from ..Documents import Datapoint

import logging, numpy
from sklearn.neural_network import MLPClassifier

class RelationModel:
    """ The model the learns the sentence embeddings for a particular relationship """

    alpha = 0.0001
    structure = (900, 50, 20)

    @classmethod
    def setParameters(cls, alpha: float, shape: tuple):
        cls.alpha = alpha if alpha else cls.alpha
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

    def predict(self, points):

        if not points: return points
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
            point.probability = float(prob[list(self.classifier.classes_).index(pred)])

        processedPoints = []

        # Verify the points
        while points:

            # Extract each point
            point = points.pop()

            # Find any duplicate relations
            duplicates = [p for p in points if point == p]

            # Extract them and remove them from the orginal structure
            for p in duplicates:
                del points[points.index(p)]

            while duplicates:

                # Iteratively record out of the duplicated points the one with the greatest probability
                dup = duplicates.pop()
                point = point if point.probability > dup.probability else dup

            # Store the winner
            processedPoints.append(point)

        return processedPoints