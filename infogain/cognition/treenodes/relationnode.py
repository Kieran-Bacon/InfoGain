import re

from ..evaltrees import EvalTree
from .conceptnode import ConceptNode

from .decorators import scenario_consistent

class RelationNode(EvalTree):
    """ Represent a relation instance between two concepts

    Params:
        domain (ConceptNode): A representation of the domain object
        relation (str): The string representation for the relationship
        target (ConceptNode): A representation of the target object

    """

    expression = re.compile(r"({0})=([\w_]+)=({0})|({0})-([\w_]+)-({0})".format(EvalTree.concept_syntax.pattern))

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

    @scenario_consistent
    def eval(self, **kwargs):
        confidence = kwargs["engine"].inferRelation(
            self.domain.instance(**kwargs),
            self.relation,
            self.target.instance(**kwargs),
            evaluate_conditions = kwargs.get("evaluate_conditions", True)
        )
        if confidence is None: return 0.
        return confidence if self.isPositive else 1. - confidence

    @staticmethod
    def split(expression):
        if "=" in expression:
            return (*expression.split("="), True)
        else:
            return (*expression.split("-"), False)