from ..exceptions import MissingConcept
from .concept import Concept
from .instance import Instance
from .rule import Rule

import logging
log = logging.getLogger(__name__)

class Relation:
    """ A relation expresses a connection between concepts.
    # TODO fix this
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
        if type(domain) is not type(target): raise ValueError("Passed incompatible types - domain: '{}' target: '{}'".format(repr(domain), repr(target)))
        if self.differ and domain == target: return False

        if isinstance(domain, Concept):
            if Concept.ABSTRACT == (domain.category or target.category): return False
            return target in self._between.get(domain, [])
        elif isinstance(domain, Instance):
            group = self._between[domain.name] if domain.name in self._between else self._between.get(domain.concept)
            if group is None: return False
            else: return True if {target.concept, target.name}.intersection(group) else False

    def subscribe(self, concept: Concept) -> None:  # TODO Improve documentation
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
        # TODO: Documentation
        if self._rules == []: return self._rules.append(rule)  # Empty collection

        for i, relRule in enumerate(self._rules):
            if rule.confidence > relRule.confidence: break
        self._rules = self._rules[:i] + [rule] + self._rules[i:]

    def rules(self, domain: Concept = None, target: Concept = None) -> [Rule]:
        # TODO: Documentation

        if domain is None and target is None:
            return list(self._rules)

        if not self.between(domain, target): return []
        return [rule for rule in self._rules if rule.applies(domain, target)]

    def assignRules(self, collection: [Rule]) -> None:
        """ Assign a collection of rules to the relation, overwritting the old rules during the
        operation
        """
        self._rules = sorted(collection, key = lambda x: x.confidence)

    def _collapse_domain_targets(self) -> (list, list):
        """ Collapse the mappings between the domains and targets into their expressive initial state. Instead of having
        a dictionary that links a single domain to a collection of targets, returned is a collection of collections of
        domains that point to a collection of a collection of targets

        Returns:
            list: Ordered domains sets that link to
            list: Ordered targets sets
        """

        minDoms, minTars = [], []  # The minimised relation sets

        for domain, targets in self._between.items():

            targets = frozenset(Concept.minimiseConceptSet(targets))

            if targets in minTars:
                minDoms[minTars.index(targets)].add(domain)
            else:
                minDoms.append({domain})
                minTars.append(targets)

        minDoms = [Concept.minimiseConceptSet(domSet) for domSet in minDoms]

        return minDoms, minTars

    def minimise(self) -> dict:
        """ Return only the information the relation represents """

        minDoms, minTars = self._collapse_domain_targets()

        # Form the relations and minimise the domains
        minDoms = sorted([sorted([con if isinstance(con, str) else con.name for con in domSet]) for domSet in minDoms])
        minTars = sorted([sorted([con if isinstance(con, str) else con.name for con in tarSet]) for tarSet in minTars])

        minimised = {"domains": minDoms, "name": self.name, "targets": minTars}

        # Collapse the rules down
        rules = [rule.minimise() for rule in self._rules]

        if self.differ: minimised["differ"] = True
        if rules: minimised["rules"] = rules

        return minimised

    def clone(self):
        domains, targets = self._collapse_domain_targets()
        return Relation(domains, self.name, targets, [rule.clone() for rule in self._rules], self.differ)