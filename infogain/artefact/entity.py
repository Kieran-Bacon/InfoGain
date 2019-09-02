import collections

class EntityProperties(collections.abc.MutableMapping):

    def __init__(self):
        self._elements = {}

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError("Attribute key must be string")
        self._elements[key] = value

    def __getitem__(self, key): return self._elements[key]
    def __delitem__(self, key): del self._elements[key]


class Entity:

    def __init__(self, classType: str, surfaceForm: str, confidence: float = 1.):
        self._classType = classType
        self._surfaceForm = surfaceForm
        self._confidence = None
        self.confidence = confidence

        self._properties = EntityProperties()

    @property
    def classType(self): return self._classType
    @property
    def surfaceForm(self): return self._surfaceForm
    @property
    def confidence(self): return self._confidence
    @confidence.setter
    def confidence(self, conf: float):
        if not isinstance(conf, float) or not 0. <= conf <= 1.:
            raise ValueError("Cannot set confidence of entity - must be float between 0-1")
        self._confidence = conf

    @property
    def properties(self): return self._properties