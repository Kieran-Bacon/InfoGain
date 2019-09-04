import weakref

from .entity import Entity

class Annotation:

    POSITIVE = 10
    INSUFFICIENT = 0
    NEGATIVE = -10

    def __init__(
        self,
        domain: Entity,
        annotationType: str,
        target: Entity,
        *,
        classification: int = None,
        confidence: float = 1.,
        annotation: str = None
        ):
        self.domain = domain
        self._annotationType = annotationType
        self.target = target

        self.confidence = confidence

        if classification is None: self._classification = None
        else: self.classification = classification

        if annotation is None: self._annotation = None
        else: self.annotation = annotation

        self._contextOwner = None
        self._context = None
        self._embedding = None

    def __str__(self):
        return "<Annotation: {} {} {} {}%>".format(self.domain, self.annotationType, self.target, self.confidence)

    @property
    def domain(self): return self._domain
    @domain.setter
    def domain(self, entity):
        if isinstance(entity, Entity): self._domain = entity
        else: raise ValueError("Annotation domain must be an Entity not '{}'".format(type(entity)))
    @property
    def annotationType(self): return self._annotationType
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
    def classification(self, classtype: int):
        if any(classtype is annType for annType in (self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE)):
            self._classification = classtype
        else:
            raise TypeError("Provided classification class was not a valid type '{}'".format(classtype))

    @property
    def annotation(self): return self._annotation
    @annotation.setter
    def annotation(self, anntype):
        if any(anntype is classType for classType in (self.POSITIVE, self.INSUFFICIENT, self.NEGATIVE)):
            self._annotation = anntype
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
