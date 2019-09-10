import weakref

from .entity import Entity

class Annotation:

    POSITIVE = 1
    INSUFFICIENT = 0
    NEGATIVE = -1

    _CLASSMAPPER = {
        POSITIVE: "POSITIVE",
        INSUFFICIENT: "INSUFFICIENT",
        NEGATIVE: "NEGATIVE"
    }

    def __init__(
        self,
        domain: Entity,
        name: str,
        target: Entity,
        *,
        classification: int = None,
        confidence: float = 1.
        ):
        self.domain = domain
        self._name = name
        self.target = target

        self.confidence = confidence

        if classification is None: self._classification = None
        else: self.classification = classification

        self._contextOwner = None
        self._context = None
        self._embedding = None

    def __repr__(self):

        prediction = ''
        if self.classification is not None:
            prediction = " {} {:.0%}".format(self._CLASSMAPPER[self.classification], self.confidence)

        return "<Annotation: {} {} {}{}>".format(self.domain, self.name, self.target, prediction)

    @property
    def domain(self): return self._domain
    @domain.setter
    def domain(self, entity):
        if isinstance(entity, Entity): self._domain = entity
        else: raise ValueError("Annotation domain must be an Entity not '{}'".format(type(entity)))
    @property
    def name(self): return self._name
    @property
    def target(self): return self._target
    @target.setter
    def target(self, entity):
        if isinstance(entity, Entity): self._target = entity
        else: raise ValueError("Annotation target must be an Entity not '{}'".format(type(entity)))

    @property
    def confidence(self): return self._confidence
    @confidence.setter
    def confidence(self, value):
        if isinstance(value, float) and 0. <= value <= 1.:
            self._confidence = value
        else:
            raise ValueError("Invalid confidence set on annotation '{}'".format(value))

    @property
    def classification(self): return self._classification
    @classification.setter
    def classification(self, classification: int):
        for classtype in (self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE):
            if classification == classtype:
                self._classification = classtype
                break
        else:
            raise TypeError("Provided classification class was not a valid type '{}'".format(classtype))

    @property
    def _owner(self): return self._contextOwner() if self._contextOwner is not None else None
    @_owner.setter
    def _owner(self, owner: weakref.ref):
        self._contextOwner = owner
        self._context = None
        self._embedding = None

    @property
    def context(self):
        if self._owner is None: return None
        return (
            self._owner.content[slice(*self._context[0])].strip(),
            self._owner.content[slice(*self._context[1])].strip(),
            self._owner.content[slice(*self._context[2])].strip()
        )

    @context.setter
    def context(self, context: ((int, int))):

        if self._context is not None:
            raise ValueError("Cannot edit context of an annotation - determined by the owning document")

        self._context = context

    @property
    def embedding(self): return self._embedding
    @embedding.setter
    def embedding(self, embeddings: ([int])):

        if self._context is None:
            raise RuntimeError("Cannot set embeddings for annotation context as context is not set")

        self._embedding = embeddings
