from ..exceptions import ConsistencyError
from . import IncompleteDatapoint

class Datapoint:
    """ An object to contain the information surrounding a single text relation.

    Params:
        data (dict) - A dictionary of data point information, very relaxed in its requirement
    """

    POSITIVE = 1
    INSUFFICIENT = 0
    NEGATIVE = -1

    def __init__(self, data: dict = {}):

        # The relation information
        self.domain = data.get("domain", None)
        self.relation = data.get("relation", None)
        self.target = data.get("target", None)

        # The textual information of the data point
        self.text = data.get("text", None)  # The full text snippet
        self.context = data.get("context", None)  # The context break down
        self.embedding = data.get("embedding", None)  # The context embedding

        # Classification values
        self.annotation = data.get("annotation", None)  # The human annotated class
        self.prediction = data.get("prediction", None)  # The predicted class
        self.probability = data.get("probability", None)  # The probability of the prediction

    def __repr__(self):
        return "<Datapoint: {}({}) {} {}({}) - emb: {}, ann: {}, pred: {}, prob: {}>".format(
            self.domain["concept"],
            self.domain["text"],
            self.relation,
            self.target["concept"],
            self.target["text"],
            True if self.embedding is not None else False,
            self.annotation,
            self.prediction,
            self.probability
        )

    def __eq__(self, other):

        checks = [
            self.domain == other.domain,
            self.target == other.target,
            self.relation == other.relation,
            self.text == other.text
        ]

        return all(checks)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(" ".join(
            [self.domain["concept"],
            self.domain["text"],
            self.relation,
            self.target["concept"],
            self.target["text"],
            self.text]))

    @property
    def annotation(self): return self._annotation
    @annotation.setter
    def annotation(self, ann: int):
        if ann is None:
            self._annotation = None
            return

        if ann not in [self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE]:
            raise ConsistencyError("Datapoint class unrecognised - {}".format(ann))

        if ann == 1: self._annotation = self.POSITIVE
        elif ann == 0: self._annotation = self.INSUFFICIENT
        else: self._annotation = self.NEGATIVE

    @property
    def prediction(self): return self._prediction
    @prediction.setter
    def prediction(self, pred: float):
        if pred is None:
            self._prediction = None
            return

        if pred not in [self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE]:
            raise ConsistencyError("Datapoint class unrecognised - {}".format(pred))

        if pred == 1: self._prediction = self.POSITIVE
        elif pred == 0: self._prediction = self.INSUFFICIENT
        else: self._prediction = self.NEGATIVE

    @property
    def probability(self): return self._probability
    @probability.setter
    def probability(self, prob: float):
        if prob is None:
            self._probability = None
            return

        if not isinstance(prob, float) or prob < 0 or prob > 1:
            raise ConsistencyError("Datapoint initialised with invalid probability - {}".format(prob))

        self._probability = prob

    def embedContext(self, embedder: object) -> None:
        """ Embed the context text according to the embedder function

        Params:
            embedder (function) - Takes a string and returns a numpy array that represents a real
                vector representation of the string

        Raises:
            IncompleteDatapoint - If the data point doesn't have any contextual information to
                embed - provide context to fix.
        """
        if self.context is None:
            raise IncompleteDatapoint("Attempted to embed a point with no context information")

        from .document import Document
        self.embedding = {key: embedder(Document.clean(context))
            for key, context in self.context.items()}

    def features(self):
        """ Collect the embedding information of the data point.

        Returns:
            [numpy.array]*3 - The left, middle and right embeddings
            annotation - The annotation of the data point

        Raises:
            IncompleteDatapoint - If the data point hasn't yet been embedded.
        """
        if self.embedding is None:
            raise IncompleteDatapoint("Datapoint has not been embedded")
        return ([
            self.embedding["left"],
            self.embedding["middle"],
            self.embedding["right"]], self.annotation)

    def clone(self):
        """ Clone the datapoint object """

        datapoint = Datapoint(self.minimise().copy())
        if self.embedding is not None:
            datapoint.embedding = self.embedding.copy()
        return datapoint

    def minimise(self) -> dict:
        """ Minimise the relevant information about the data point.

        Returns:
            dict - The revelant information
        """
        return {
            "domain": self.domain,
            "target": self.target,
            "relation": self.relation,
            "text": self.text,
            "context": self.context,
            "annotation": self.annotation,
            "prediction": self.prediction,
            "probability": self.probability
        }