from .Concept import Concept
from .Relation import Relation
from .Language import *

class Fact:

    def __init__(self, domain, relation, target, confidence):

        self.domain = domain
        self.relation = relation
        self.target = target
        self.confidence = confidence

        self.conditions = set()
        self.unbound = {}

    def addCondition(self, condition) -> None:

        if conditon in self.conditions:
            raise ValueError("Attempt to overwrite condition in fact")

        self.conditions.add(condition)

    def scenarios(self, domain, target):

        keys = []
        concepts = []

        for k, c in self.unbound.items():
            keys.append(k)
            concepts.append([c] + list(c.descendants()))

        




        pass