import collections

from ..exceptions import MissingConcept
from .concept import Concept, ConceptSet
from .instance import Instance
from .rule import Rule

import logging
log = logging.getLogger(__name__)

class Relation:
    """ A relation expresses a connection between concepts. It declares how particular concepts interact and informs
    other system functionality.

    Params:
        domains (set): A collection of concepts
        name (str): The name to identify the relation object
        targets (set): A collection of concepts
        rules ([Rule]): Rules that determine when the relation holds between concepts
        differ (bool): toggle for where a relation holds between a concept and itself
    """

    def __init__(self, domains: {Concept}, name: str, targets: {Concept}, rules=[], differ: bool = False):

        self.name = name
        self._concepts = RelationConceptManager(self, domains, targets)
        self.rules = rules
        self.differ = differ

    @property
    def concepts(self): return self._concepts
    @property
    def domains(self): return ConceptSet([con for g in self.concepts.domains for con in g])
    @property
    def targets(self): return ConceptSet([con for g in self.concepts.targets for con in g])
    @property
    def rules(self): return self._rules
    @rules.setter
    def rules(self, rules: [Rule]): self._rules = RuleManager(self, rules)


    def __str__(self):
        return " ".join([str({str(x) for x in self.concepts.domains}), self.name, str({str(x) for x in self.concepts.targets})])

    def between(self, domain: Concept, target: Concept) -> bool:
        """ Verify if the relationship holds between two concepts.

        Params:
            domain (Concept): A potential domain of the relation
            target (Concept): A potential target of the relation

        Returns:
            bool: True if relation holds between the domain and target provided
        """
        if type(domain) is not type(target):
            raise ValueError("Passed incompatible types - domain: '{}' target: '{}'".format(repr(domain), repr(target)))
        if self.differ and domain == target: return False

        if isinstance(domain, Concept):
            # Ensure that the concepts can even be compared
            if Concept.ABSTRACT == (domain.category or target.category): return False
        elif isinstance(domain, Instance):
            # Switch the instances for their parents
            domain, target = domain.concept, target.concept

        # Loop through the various sets to check, return once found or
        for domains, targets in self.concepts:
            if domain in domains and target in targets: return True
        return False

    def subscribe(self, concept: Concept) -> None:
        """ Add the concept object into the relation, correctly mapping the concept to targets, or domains to the
        concept where applicable.

        Params:
            concept (Concept): the concept to be added
        """

        # Get the ancestors of the concept
        ancestors = concept.ancestors()

        # For all the concept sets check where the concept should be added
        for i, (domains, targets) in enumerate(self.concepts):
            if ancestors.intersection(domains): self.concepts.addDomain(concept, i)
            if ancestors.intersection(targets): self.concepts.addTarget(concept, i)

        # For each of the rules, pass the concept on as relevant
        for rule in self._rules: rule.subscribe(concept)

    def minimise(self) -> dict:
        """ Return only the information the relation represents """
        minimised = {
            "domains": sorted([group.minimised().toStringSet() for group in self.concepts.domains]),
            "name": self.name,
            "targets": sorted([group.minimised().toStringSet() for group in self.concepts.targets])
        }

        # Record non-default parameters
        if self.differ: minimised["differ"] = True
        if self._rules: minimised["rules"] = [rule.minimise() for rule in self._rules]

        return minimised

    def clone(self):
        return Relation(
            self.concepts.domains,
            self.name,
            self.concepts.targets,
            [rule.clone() for rule in self._rules],
            self.differ
        )

class RelationConceptManager(collections.abc.MutableSequence):

    def __init__(self, owner: Relation, domains: object = None, targets: object = None):
        self._owner = owner
        self.domains = []
        self.targets = []

        self._members = {}
        self._memberCount = collections.Counter()

        if domains and targets:
            # Test for domain and target set up
            example = next(iter(domains))
            if isinstance(example, (str, Concept)):
                # A single mapping from domains to targets
                self.append((domains, targets))
            else:
                # A collection of mappings from domains to targets
                for group in zip(domains, targets): self.append(group)

    def _pad(self, index):
        """ Ensure that the domain groups and target groups have content up to the provided index """
        for _ in range(index - (len(self.domains)-1)):
            self.domains.append(ConceptSet())
            self.targets.append(ConceptSet())

    def __getitem__(self, index: int):
        self._pad(index)
        return (self.domains[index], self.targets[index])
    def __setitem__(self, index: int, conceptSetTuple: tuple):
        """ Set a specific domain and target set. """
        self.insert(index, conceptSetTuple)

    def insert(self, index: int, conceptSetTuple: (ConceptSet, ConceptSet)):
        self.domains.insert(index, ConceptSet())
        self.targets.insert(index, ConceptSet())

        domains, targets = conceptSetTuple
        for con in domains: self.addDomain(con, index)
        for con in targets: self.addTarget(con, index)

    def append(self, conceptSetTuple: (ConceptSet, ConceptSet)):

        index, (domains, targets) = len(self), conceptSetTuple
        for con in domains: self.addDomain(con, index)
        for con in targets: self.addTarget(con, index)

    def __delitem__(self, index: int):
        for dom in self.domains[index].copy(): self.removeDomain(dom, index)
        for tar in self.targets[index].copy(): self.removeTarget(tar, index)

        del self.domains[index]
        del self.targets[index]

    def __len__(self): return len(self.domains)
    def __iter__(self): return zip(self.domains, self.targets)

    def addDomain(self, concept: Concept, index: int = None): self._add(self.domains, concept, index)
    def addTarget(self, concept: Concept, index: int = None): self._add(self.targets, concept, index)
    def _add(self, collection: [ConceptSet], concept: Concept, index: int, include_descendants: bool = True):

        if concept not in self._members:
            if isinstance(concept, Concept):
                # Add the concept as a member of this class
                self._members[concept.name] = concept

                # Inform the concept that it is now a part of this relationship
                concept._relationMembership.add(self._owner)

            elif isinstance(concept, str):
                self._members[concept] = None
            else:
                raise ValueError("Invalid item passed to relation's conceptset - str or Concept only")

        # Add each child of the concept into this relationship when applicable
        if include_descendants and isinstance(concept, Concept):
            for child in concept.descendants():
                self._add(collection, child, index, False)

        # If an index was given, add the concept into that index
        if index is not None:
            self._pad(index)
            collection[index].add(concept)
        else:
            for group in collection: group.add(concept)

    def removeDomain(self, concept: Concept, index: int = None): self._remove(self.domains, concept, index)
    def removeTarget(self, concept: Concept, index: int = None): self._remove(self.targets, concept, index)
    def _remove(self, collection: list, concept: Concept, index: int = None, include_ancestors: bool = True):

        # If concept not known to concept, return immediately
        if concept not in self._members: return

        # Unpack the
        if isinstance(concept, Concept):
            name = concept.name

            # Remove all parents of the concept at the same time for relation consistency
            if include_ancestors:
                for parent in concept.ancestors():
                    self._remove(collection, parent, index, False)
        else:
            name = concept

        if index is not None:
            conceptSet = collection[index]

            if concept in conceptSet:
                conceptSet.discard(concept)

                self._memberCount[name] -= 1
        else:
            for conceptSet in collection:
                conceptSet.discard(concept)

            self._memberCount[name] = 0

        if self._memberCount[name] == 0:
            del self._members[name]
            del self._memberCount[name]

            # Remove this relationship from the concept as it is no longer a member
            if isinstance(concept, Concept):
                concept._relationMembership.remove(self._owner)

    def partials(self) -> {str}:
        """ Provide a set of the partial concepts within the set

        Returns:
            {str}: A set of concept names yet to be linked correctly
        """
        partials = {con for rule in self._owner.rules for group in [rule.domains, rule.targets] for con in group.partials()}
        return partials.union({con for group in self.domains + self.targets for con in group.partials()})

class RuleManager(collections.abc.MutableSequence):

    def __init__(self, owner: Relation, rules: list = []):
        self._owner = owner
        self._elements = rules.copy()

    def __call__(self, domain: Concept, target: Concept):
        """ Collect the rules within the relation, if domain and target is passed, collect together only rules that
        apply to those concepts. Perform a sanity check within the relation first to avoid unnecessary checking.

        Params:
            domain (Concept) = None: Domain concept
            target (Concept) = None: Target concept

        Returns:
            [Rule]: A list of rules of the relation or that apply to the scenario
        """
        if not self._owner.between(domain, target): return []
        return [rule for rule in self._elements if rule.applies(domain, target)]

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __setitem__(self, index: int, rule: Rule): self.insert(index, rule)
    def __getitem__(self, index: int): return self._elements[index]
    def __delitem__(self, index: int): del self._elements[index]
    def __contains__(self, rule: Rule): return rule in self._elements
    def insert(self, index: int, rule: Rule): self._elements.insert(index, rule)

    def add(self, rule: Rule):
        """ Add a Rule object to the relation, order the rule correctly based on confidence

        Params:
            rule (Rule): The rule
        """
        i = 0
        for i, relRule in enumerate(self._elements):
            if rule.confidence >= relRule.confidence: break
        else:
            i += 1
        self._elements.insert(i, rule)

    def remove(self, rule: Rule):
        self._elements.remove(rule)