from . import IncompleteDatapoint
from .DocumentOperations import cleanSentence

class Datapoint:

    def __init__(self, data: dict = {}):
        """ Initialise the datapoint information, unpack it from a dictionary item.

        Params:
            data - A dictionary of the datapoint information.
        """

        if data:

            self.domain = data.get("domain", None)
            self.relation = data.get("relation", None)
            self.target = data.get("target", None)

            self.text = data.get("text", None)
            self.context = data.get("context", None)

            self.annotation = data.get("annotation", None)
            self.prediction = data.get("prediction", None) 
            self.probability = data.get("probability", None)

            self.embedding = data.get("embedding", None)

    def __str__(self):

        string = "{}({}) {} {}({})".format(
            self.domain["concept"],self.domain["text"], self.relation, self.target["concept"],self.target["text"])

        scores = [str(score) for score in [self.annotation, self.prediction, self.probability] if not score is None]

        return " ".join([string]+scores)

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
        return hash(" ".join([self.domain["concept"], self.domain["text"], self.relation, self.target["concept"], self.target["text"], self.text])) 

    def embedContext(self, embedder: object) -> None:
        """ Embed the context text according to the embedder function """
        if self.context is None:
            raise IncompleteDatapoint("Attempted to embed a point with no context information")
        self.embedding = {key: embedder(cleanSentence(context)) for key, context in self.context.items()}

    def features(self):
        if self.embedding is None:
            raise IncompleteDatapoint("Attempting to collect feature information when none available")
        return [self.embedding["left"], self.embedding["middle"], self.embedding["right"]], self.annotation

    def minimise(self) -> dict:
        struct = {
            "domain": self.domain,
            "target": self.target,
            "relation": self.relation,
            "text": self.text,
            "context": self.context,
            "annotation": self.annotation,
            "prediction": self.prediction,
            "probability": self.probability
        }

        return struct