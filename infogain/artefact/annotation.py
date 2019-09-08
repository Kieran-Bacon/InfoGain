import weakref

from .entity import Entity

class Annotation:

    POSITIVE = 10
    INSUFFICIENT = 0
    NEGATIVE = -10

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
        confidence: float = 1.,
        annotation: str = None
        ):
        self.domain = domain
        self._name = name
        self.target = target

        self.confidence = confidence

        if classification is None: self._classification = None
        else: self.classification = classification

        if annotation is None: self._annotation = None
        else: self.annotation = annotation

        self._contextOwner = None
        self._context = None
        self._embedding = None

    def __repr__(self):

        title = "Annotation"
        if self.annotation is not None:
            title = "Annotation({})".format(self._CLASSMAPPER[self.annotation])

        prediction = ''
        if self.classification is not None:
            prediction = " {} {:.0%}".format(self._CLASSMAPPER[self.classification], self.confidence)

        return "<{}: {} {} {}{}>".format(title, self.domain, self.name, self.target, prediction)

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
    def annotation(self): return self._annotation
    @annotation.setter
    def annotation(self, anntype):
        for classtype in (self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE):
            if anntype == classtype:
                self._annotation = classtype
                break
        else:
            raise TypeError("Provided annotation class was not a valid type '{}'".format(anntype))

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
