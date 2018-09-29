class ConsistencyError(Exception):
    pass

from .instance import ConceptInstance, RelationInstance
from .inferenceengine import InferenceEngine