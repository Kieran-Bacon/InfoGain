from ..knowledge import Ontology, Relation, Rule
from .evalrule import EvalRule

class EvalRelation(Relation):

    def addRule(self, rule: Rule) -> None:
        if isinstance(rule, Rule): rule = EvalRule.fromRule(rule, self._engine)
        Relation.addRule(self, rule)

    @classmethod
    def fromRelation(cls, relation: Relation):
        """ Convert a relation into an evaluable relation object """

        return EvalRelation(
            relation.domains,
            relation.name,
            relation.targets,
            rules = [
                EvalRule.fromRule(rule) for rule in relation.rules
            ],
            differ = relation.differ
        )