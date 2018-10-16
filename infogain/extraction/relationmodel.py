from ..artefact import Datapoint
from ..knowledge import Relation

import logging, numpy
from sklearn.neural_network import MLPClassifier

import logging
log = logging.getLogger(__name__)

class RelationModel:
    """ The model that represents a single relation classifier
    
    Params:
        name (str) - The name of the relation the model represents
     """

    alpha = 0.0001
    structure = (900, 50, 20)

    @classmethod
    def setParameters(cls, alpha: float, shape: tuple) -> None:
        """ Set the default parameters for the generation of all relation models. Ensures that
        relations are constructed in the same manner 

        Params:
            alpha (float) - The alpha value for backpropergation in the Neural Network
            shape ((int,)) - The network size and shape
        """
        cls.alpha = alpha if alpha else cls.alpha
        cls.structure = shape

    def __init__(self, name: str):
        self.name = name
        self.classifier = MLPClassifier(hidden_layer_sizes=RelationModel.structure)
        self.fitted = False

    def fit(self, datapoints: [Datapoint]) -> None:
        """ Use the datapoints to train the relation model
        
        Params:
            datapoints (Datapoint) - A collection of datapoints for this relation to train on
        """

        # Do nothing if no datapoints have been provided
        if not len(datapoints):
            log.warning("Fitting Relation model for '"+self.name+"' without any datapoints")
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

    def predict(self, points: [Datapoint]) -> [Datapoint]:
        """ Use the relation model to predict on a collection of points and return the points

        Params:
            points (Datapoint) - A collection of datapoints to be predicted on
        """

        if not points: return points
        if not self.fitted:
            log.error("Attempt to predict on unfitted relation model: " + self.name)
            return points

        # Extract data point feature information
        Xte = []
        for point in points:
            x, _ = point.features()
            Xte.append(numpy.concatenate(x))

        # Predict on the data
        predictions = self.classifier.predict(Xte)
        probabilities = self.classifier.predict_proba(Xte)

        # Determine the prediction class and record the probability of that selection
        for point, pred, prob in zip(points, predictions, probabilities):
            assert(pred == int(pred))
            point.prediction = int(pred)
            point.probability = float(prob[list(self.classifier.classes_).index(pred)])

        processedPoints = []  # The processed datapoints 

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