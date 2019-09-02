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
        self._domain = domain
        self._annotationType = annotationType
        self._target = target


        self.confidence = confidence
        if classification is None: self._classification = None
        else: self.classification = classification
        if annotation is None: self._annotation = None
        else: self.annotation = annotation

        self._contextOwner = None
        self._context = None

    @property
    def domain(self): return self._domain
    @property
    def annotationType(self): return self._annotationType
    @property
    def target(self): return self._target

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
    def _owner(self): return self._contextOwner
    @_owner.setter
    def _owner(self, owner):
        self._contextOwner = owner
        self._context = None

    @property
    def context(self):
        return (
            self._contextOwner.content[slice(*self._context[0])],
            self._contextOwner.content[slice(*self._context[1])],
            self._contextOwner.content[slice(*self._context[2])]
        )

    @context.setter
    def context(self, context: ((int, int))):

        if self._context is not None:
            raise ValueError("Cannot edit context of an annotation - determined by the owning document")

        self._context = context
