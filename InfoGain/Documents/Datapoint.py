import InfoGain.Documents.DocumentOperations as DO

class Datapoint:

    def __init__(self, data: dict = None):
        """ Initialise the datapoint information, unpack it from a dictionary item.

        Params:
            data - A dictionary of the datapoint information.
        """

        self.annotation, self.prediction, self.predProb = None, None, None

        self.embedded = False
        self.lContextEmbedding, self.mContextEmbedding, self.rContextEmbedding = None, None, None

        if not data is None:
            # Set the datapoint concepts
            self.domain, self.domainRepr = data["domain"]["concept"], data["domain"]["text"]
            self.target, self.targetRepr = data["target"]["concept"], data["target"]["text"]
            self.relation = data["relation"]

            # The complete, original text, the datapoint represents
            self.text = data["text"]

            # The context around the word
            self.lContext = data["context"]["left"]
            self.mContext = data["context"]["middle"]
            self.rContext = data["context"]["right"]

            # The datapoint's class definition
            self.annotation = data.get("annotation", None)

    def __str__(self):
        return " ".join([self.domainRepr, self.relation, self.targetRepr, str(self.annotation), str(self.prediction), str(self.predProb)])

    def __eq__(self, other):

        checks = [
            self.domain == other.domain,
            self.domainRepr == other.domainRepr,
            self.target == other.target,
            self.targetRepr == other.targetRepr,
            self.relation == other.relation,
            self.text == other.text,
            self.lContext == other.lContext,
            self.mContext == other.mContext,
            self.rContext == other.rContext
        ]

        return all(checks)

    def __ne__(self, other):
        return not self.__eq__(other)    

    def setDomain(self, concept: str, textrepr: str):
        """ Set the domain and the identify the representation in the text that it orginiated from """
        self.domain, self.domainRepr = concept, textrepr

    def setTarget(self, concept: str, textrepr: str):
        self.target, self.targetRepr = concept, textrepr

    def setRelation(self, relname: str):
        """ Set the relationship id of the datapoint """
        self.relation = relname

    def setText(self, text: str):
        self.text = text

    def setContext(self, left: str, middle: str, right: str):
        self.lContext, self.mContext, self.rContext = left, middle, right

    def setAnnotation(self, annotation: bool) -> None:
        """ Set the datapoint annotation class """
        self.annotation = annotation

    def embedContext(self, embedder: object) -> None:
        """ Embed the context text according to the embedder function """
        self.lContextEmbedding = embedder(DO.cleanSentence(self.lContext))
        self.mContextEmbedding = embedder(DO.cleanSentence(self.mContext))
        self.rContextEmbedding = embedder(DO.cleanSentence(self.rContext))
        self.embedded = True

    def features(self):
        if not self.embedded:
            raise Exception("Embeddings not set for this datapoint")

        return [self.lContextEmbedding,self.lContextEmbedding,self.lContextEmbedding], self.annotation

    def isDuplicate(self, point) -> bool:
        """ Check if another point expresses the same relationship for the same segment of a document """

        return (self.domainRepr == point.domainRepr and
            self.targetRepr == point.targetRepr and
            self.relation == point.relation and
            self.text == point.text)

    def minimise(self) -> dict:
        struct = {
            "domain": {
                "concept": self.domain,
                "text": self.domainRepr
            },
            "target": {
                "concept": self.target,
                "text": self.targetRepr
            },
            "relation": self.relation,
            "text": self.text,
            "context": {
                "left": self.lContext,
                "middle": self.mContext,
                "right": self.rContext
            },
            "annotation": self.annotation
        }

        return struct