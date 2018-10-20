import re

from ..evaltrees import EvalTree
from .conceptnode import ConceptNode


class RelationNode(EvalTree):

    expression = re.compile(r"({0})=([\w_]+)=({0})|({0})-([\w_]+)-({0})".format(ConceptNode.expression.pattern))
    
    def __init__(self, domain: ConceptNode, relation: str, target: ConceptNode, isPositive: bool):
        self.domain = domain
        self.relation = relation
        self.target = target
        self.isPositive = isPositive

    def __str__(self):
        link = "=" if self.isPositive else "-"
        return link.join([str(self.domain), self.relation, str(self.target)])

    def parameters(self):
        return self.domain.parameters().union(self.target.parameters())

    def eval(self, **kwargs):
        confidence = self.engine.inferRelation(
            self.domain.instance(**kwargs),
            self.relation,
            self.target.instance(**kwargs),
            evaluate_conditions = "facts_only" in kwargs
        )
        return confidence if self.isPositive else (-1)*confidence #(100.0-confidence)

    @staticmethod
    def split(expression):
        if "=" in expression:
            return (*expression.split("="), True)
        else:
            return (*expression.split("-"), False)