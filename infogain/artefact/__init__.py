class EmptyDocument(Exception): pass
class IncompleteDatapoint(Exception): pass

from .entity import Entity
from .annotation import Annotation
from .document import Document