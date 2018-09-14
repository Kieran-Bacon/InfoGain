from .concept import Concept
from .relation import Relation

class Fact:
    """ A fact that asserts some information """
    
    def __init__(self, domain: Concept, relation: Relation, target: Concept, annotation: int, confidence: float):
        self.domain = domain
        self.relation = relation
        self.target = target
        self.annotation = annotation
        self.confidence = confidence