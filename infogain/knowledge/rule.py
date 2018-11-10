import collections

from .concept import Concept
from .instance import Instance

class Condition:

    def __init__(self, logic: str, salience: float = 100):
        self.logic = logic
        self.salience = salience

    def __str__(self): return self.logic
    def __repr__(self): return "<Condition: '{}' with salience {}>".format(self.logic, self.salience)
    def __hash__(self): return hash(self.logic)
    def __eq__(self, other): self.logic == other
    def __ne__(self, other): not self.__eq__(other)

    def containsDomain(self): return "%" in self.logic
    def containsTarget(self): return "@" in self.logic

    def minimise(self): return {"logic": self.logic, "salience": self.salience}
    def clone(self): return Condition(self.logic, self.salience)

class Rule:
    """ A rule is used to express how a relation might come about given a collection of knowledge """
    # TODO: Complete documentation for Rule

    def __init__(self, domains: {Concept}, targets: {Concept}, confidence: float, supporting: bool = True, conditions: [Condition] = []):

        # Copy the contents of the two sets as to ensure decoupling
        self.domains = set(domains) if isinstance(domains, collections.Iterable) else {domains}
        self.targets = set(targets) if isinstance(domains, collections.Iterable) else {targets}
        self.confidence = confidence
        self.supporting = supporting

        if isinstance(self.supporting, list): raise ValueError("Its happened")

        for i, condition in enumerate(conditions):
            if isinstance(condition, dict) and all([key in condition for key in ["logic", "salience"]]):
                conditions[i] = Condition(condition["logic"], condition["salience"])


        self._conditions = sorted(conditions, key = lambda x: x.salience)

        if conditions:
            self.domains = Concept.expandConceptSet(self.domains)
            
            if any([condition.containsTarget() for condition in conditions]):
                self.targets = self.targets.union(Concept.expandConceptSet(self.targets))

            self.targets = Concept.expandConceptSet(self.targets, descending=False)

    def __str__(self):
        base = " ".join([str([str(d) for d in self.domains]), str([str(d) for d in self.targets]), "is true with", str(self.confidence)])
        if self._conditions:
            base += " when:\n"
            base += "\n".join([str(condition) for condition in self._conditions])

        return base

    def applies(self, domain: (Concept), target: (Concept)): # TODO Documentation
        """ Determine if the rule applies to the the domain and target pairing that has been
        provided """

        # Ensure that the arguments are compariable
        if type(domain) is not type(target):
            raise ValueError("The domain and range passed have different types: {}({}) and {}({}) respectively".format(
                type(domain), domain, type(target), target
            ))

        # Quick check before search whether or not the concepts are viable 
        if isinstance(domain, Concept) and (Concept.ABSTRACT is (domain.category or target.category)): return False

        # Expanded search for instances
        if isinstance(domain, Instance):
            return ((domain in self.domains or domain.concept in self.domains) and
                    (target in self.targets or target.concept in self.targets))

        # Final search of items
        return domain in self.domains and target in self.targets

    def hasConditions(self):
        """ Deterimine of the rule has any conditions - Return True if it does, False if not """
        return len(self._conditions) > 0

    def conditions(self): # TODO document and test
        return self._conditions

    def _collapse_domain_targets(self):
        domains = sorted([c if isinstance(c, str) else c.name for c in Concept.minimiseConceptSet(self.domains)])
        targets = sorted([c if isinstance(c, str) else c.name for c in Concept.minimiseConceptSet(self.targets)])
        return domains, targets

    def minimise(self):
        """ Reduce the rule down to a dictionary object of definitions """

        domains, targets = self._collapse_domain_targets()

        minimised = {"domains": domains, "targets": targets, "confidence": self.confidence }

        if self._conditions:
            minimised["conditions"] = [condition.minimise() for condition in self._conditions]

        return minimised

    def clone(self): # TODO Documentation
        domains, targets = self._collapse_domain_targets()
        return Rule(domains, targets, self.confidence, self.supporting, [condition.clone() for condition in self._conditions])