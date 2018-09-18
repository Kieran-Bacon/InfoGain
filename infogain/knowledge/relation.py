from . import MissingConcept
from .concept import Concept
from .rule import Rule

import logging
log = logging.getLogger(__name__)

class Relation:
    """ A relation expresses a connection between concepts.
    
    Args:
        domains (set): A collection of concepts
        name (str): The name to identify the relation object
        targets (set): A collection of concepts
    """

    def __init__(self, domains: {Concept}, name: str, targets: {Concept}, rules=[], differ: bool = False):

        self.name = name
        self.domains = set()
        self.targets = set()
        self.assignRules(rules)
        self._between = {}

        self.differ = differ

        example = next(iter(domains))
        if isinstance(example, (str, Concept)):
            # A single mapping from domains to targets

            domains = Concept.expandConceptSet(domains)
            targets = Concept.expandConceptSet(targets)

            self.domains = domains
            self.targets = targets

            for dom in domains:
                self._between[dom] = set(targets)

        else:
            # A collection of mappings from domains to targets
            for doms, tars in zip(domains, targets):
                doms = Concept.expandConceptSet(doms)
                tars = Concept.expandConceptSet(tars)

                self.domains = self.domains.union(doms)
                self.targets = self.targets.union(tars)

                for dom in doms:
                    self._between[dom] = self._between.get(dom, set()).union(tars)

        log.debug("Generated relation {}".format(self))

        if not self.domains or not self.targets:
            raise MissingConcept("Relation {} generated without domain and target pairings".format(self.name))

    def __str__(self):
        return " ".join([str({str(x) for x in self.domains}), self.name, str({str(x) for x in self.targets})]) 

    def between(self, domain: Concept, target: Concept) -> bool:
        """ Verify if the relationship holds between two concepts.
        
        Params:
            domain (Concept): A potential domain of the relation
            target (Concept): A potential target of the relation
            
        Returns:
            bool: True if relation holds between the domain and target provided
        """
        if Concept.ABSTRACT == (domain.category or target.category): return False
        if self.differ and domain == target: return False
        return target in self._between.get(domain, [])

    def subscribe(self, concept: Concept) -> None:
        """ Intelligently links concept with domain or target based on 
        relative linkage """

        if concept.category == Concept.ABSTRACT : return # Ensure concept is meant to be viewable

        # Add the concept into the concept stores if one of its ancestors is present
        ancestors = concept.ancestors()

        # Check if the concept is a domain within the relation
        if self.domains.intersection(ancestors):
            
            # Determine the set of target concepts this concept will link to
            targets = set()
            for anc in self.domains.intersection(ancestors):
                targets = targets.union(self._between[anc])
            self._between[concept] = targets

            self.domains.add(concept)  # Add the concept as a domain

        # Check if the concept is a target of the relation
        if self.targets.intersection(ancestors):
            
            # Add concept to every target set where applicable
            validParents = self.targets.intersection(ancestors)
            for targetSet in self._between.values():
                if validParents.intersection(targetSet):
                    targetSet.add(concept)

            self.targets.add(concept)  # Add the concept as a target
    
    def addRule(self, rule: Rule) -> None:
        if not self._rules: self._rules.append(rule)  # Empty collection

        for i, relRule in enumerate(self._rules):
            if rule.confidence > relRule.confidence: break
        self._rules = self._rules[:i] + [rule] + self._rules[i:]

    def rules(self, domain: Concept = None, target: Concept = None) -> [Rule]:

        if domain is None and target is None:
            return list(self._rules)

        if not self.between(domain, target): return []
        return [rule for rule in self._rules if rule.applies(domain, target)]

    def assignRules(self, collection: [Rule]) -> None:
        """ Assign a collection of rules to the relation, overwritting the old rules during the
        operation
        """
        self._rules = sorted(collection, key = lambda x: x.confidence)

    def minimise(self) -> dict:
        """ Return only the information the relation represents """

        minDoms, minTars = [], []  # The minimised relation sets

        for domain, targets in self._between.items():

            targets = frozenset(Concept.minimiseConceptSet(targets))

            if targets in minTars:
                minDoms[minTars.index(targets)].add(domain)
            else:
                minDoms.append({domain})
                minTars.append(targets)

        # Form the relations and minimise the domains
        minDoms = sorted([sorted([con if isinstance(con, str) else con.name for con in Concept.minimiseConceptSet(domSet)]) for domSet in minDoms])
        minTars = sorted([sorted([con if isinstance(con, str) else con.name for con in tarSet]) for tarSet in minTars])

        minimised = {"domains": minDoms, "name": self.name, "targets": minTars}

        # Collapse the rules down
        rules = [rule.minimise() for rule in self._rules]

        if self.differ: minimised["differ"] = True
        if rules: minimised["rules"] = rules

        return minimised

    def clone(self):
        log.debug("Cloning relation object: {}".format(self.minimise()))

        minimised = self.minimise()
        minimised["rules"] = [rule.clone() for rule in self._rules]

        return Relation(**minimised)