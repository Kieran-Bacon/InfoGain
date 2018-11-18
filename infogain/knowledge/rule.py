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
    """ A rule expresses when a relation occurs and with what confidence does it occur. It references external pieces of
    information and describes the scenarios that may give rise to a Relation
    
    Params:
        domains ({Concept}): A set of domain concepts - A subset of the relation domains
        targets ({Concept}): A set of target concepts - A subset of the relation targets
        confidence (float): The confidence of the relation given its conditions

        [Keywords]
        supporting (bool): sign of the rule - If the rule, does it suggest the relation is true or false
        conditions ([Condition]): The list of conditions of the Rule, contains the logic of the rule 
    """

    def __init__(
        self,
        domains: {Concept},
        targets: {Concept},
        confidence: float,
        *,
        supporting: bool = True,
        conditions: [Condition] = []):

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

    def __repr__(self):
        confidence = self.confidence if self.supporting else self.confidence*-1
        base = "<Rule: {} {} is true with {}".format(self.domains, self.targets, confidence)
        if self._conditions:
            base += " when:\n"
            base += "\n".join([str(condition) for condition in self._conditions])

        return base

    def applies(self, domain: (Concept), target: (Concept)) -> bool:
        """ Determine if the rule applies to the the domain and target pairing that has been
        provided.
        
        Params:
            domain (Concept/Instance): The domain concept
            target (Concept/Instance): The target concept

        Returns:
            bool: True if it does apply else False

        Raises:
            ValueError: When the domain and target types don't match
        """

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

    def conditions(self):
        """ Return the conditions of the Rule """
        return self._conditions

    def _collapse_domain_targets(self):
        """ Collapse the domain and target down to their most expressive form, supports other functions """
        domains = sorted([c if isinstance(c, str) else c.name for c in Concept.minimiseConceptSet(self.domains)])
        targets = sorted([c if isinstance(c, str) else c.name for c in Concept.minimiseConceptSet(self.targets)])
        return domains, targets

    def minimise(self) -> dict:
        """ Reduce the rule down to a dictionary object that defines the rule
        
        Returns:
            dict: keys {"domains", "targets", "confidence", "supporting", "conditions"}
        """

        domains, targets = self._collapse_domain_targets()

        minimised = {"domains": domains, "targets": targets, "confidence": self.confidence }

        if self._conditions:
            minimised["conditions"] = [condition.minimise() for condition in self._conditions]
        if not self.supporting: minimised["supporting"] = self.supporting

        return minimised

    def clone(self):
        """ Generate a deep copy of this Rule - All references to concepts are replaced with strings 
        
        Returns:
            Rule: A new Rule emblematic of the original
        """
        domains, targets = self._collapse_domain_targets()
        return Rule(
            domains,
            targets,
            self.confidence,
            supporting=self.supporting,
            conditions=[condition.clone() for condition in self._conditions]
        )