from ..knowledge import Ontology, Relation, Rule
from .evalrule import EvalRule

class EvalRelation(Relation):

    def assignEngine(self, engine): self._engine = engine

    def addRule(self, rule: Rule) -> None:
        if isinstance(rule, Rule): rule = EvalRule.fromRule(rule, self._engine)
        Relation.addRule(self, rule)

    @classmethod
    def fromRelation(cls, relation: Relation, engine: Ontology):
        """ Convert a relation into an evaluable relation object """
        rules = [EvalRule.fromRule(rule, engine) for rule in relation.rules()]
        evalRelation = EvalRelation(relation.domains, relation.name, relation.targets, rules, relation.differ)
        evalRelation.assignEngine(engine)
        return evalRelation