import weakref

from ..knowledge import Ontology, Relation, Rule
from ..knowledge.relation import RuleManager

from .evalrule import EvalRule

class EvalRuleManager(RuleManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ruleMapper = {}

    def add(self, rule: Rule):
        if isinstance(rule, Rule):
            self._ruleMapper[rule] = rule = EvalRule.fromRule(rule)

        super().add(rule)

    def remove(self, rule: Rule):
        if isinstance(rule, Rule): rule = self._ruleMapper[rule]

        super().remove(rule)

class EvalRelation(Relation):

    @property
    def rules(self): return self._rules
    @rules.setter
    def rules(self, rules: list): self._rules = EvalRuleManager(weakref.ref(self), rules)


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