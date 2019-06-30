import weakref
import collections

from ..exceptions import MissingConcept
from ..information import Vertex
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

    Raises:
        AssertionError: In the event that the domains and targets aren't consistent with each other how they are
            instantiated. Either both a iterable of concepts, or both an iterable of iterables of concepts.
    """

    def __init__(self, domains: {Concept}, name: str, targets: {Concept}, rules=[], differ: bool = False):

        self.name = name
        self._domains = RelationConceptManager(self, domains, isDomain = True)
        self._targets = RelationConceptManager(self, targets, isDomain = False)
        assert len(self._domains) == len(self._targets), "Inconsistent types of domains and targets passed"
        self.rules = rules
        self.differ = differ

    @property
    def domains(self) -> ConceptSet: return self._domains
    @property
    def targets(self) -> ConceptSet: return self._targets
    @property
    def rules(self) -> list: return self._rules
    @rules.setter
    def rules(self, rules: [Rule]): self._rules = RuleManager(self, rules)

    def __repr__(self):
        return "<Relation {}: {} - {}>".format(self.name, self._domains, self._targets)

    def __str__(self):
        return " ".join([str({str(x) for x in self._domains}), self.name, str({str(x) for x in self._targets})])

    def appendConceptPairing(self, domains: ConceptSet, targets: ConceptSet) -> int:

        index = self._domains.append(domains)
        self._targets[index] = targets

        return index

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
        for domains, targets in zip(self.domains, self.targets):
            if domain in domains and target in targets: return True
        return False

    def _subscribe(self, concept: Concept) -> None:
        """ Add the concept object into the relation, correctly mapping the concept to targets, or domains to the
        concept where applicable.

        Params:
            concept (Concept): the concept to be added
        """

        # Get the ancestors of the concept
        ancestors = concept.ancestors()

        # For all the concept sets check where the concept should be added
        for domains, targets in zip(self.domains, self.targets):
            if ancestors.intersection(domains): domains._subscribe(concept)
            if ancestors.intersection(targets): targets._subscribe(concept)

        # For each of the rules, pass the concept on as relevant
        for rule in self._rules: rule._subscribe(concept)

    def _unsubscribe(self, concept: Concept):
        """ """

        # Collect the ancestors of this concept
        ancestors = concept.ancestors()

        # For all the concept sets check whether they are
        for domains, targets in zip(self.domains, self.targets):
            if concept in domains and not ancestors.intersection(domains): domains._unsubscribe(concept)
            if concept in targets and not ancestors.intersection(targets): targets._unsubscribe(concept)

        for rule in self._rules: rule._unsubscribe(concept)

    def clone(self):
        return Relation(
            self.domains,
            self.name,
            self.targets,
            [rule.clone() for rule in self._rules],
            self.differ
        )


class RelationConceptSet(ConceptSet):
    """ Concept Set

    """

    #? The ConceptSet shall own a reference to the relation, the concept shall
    #? hold a relation counter so that when we remove concepts the counter goes down
    #?

    def __init__(self, owner: Relation, iterable: collections.abc.Iterable):

        self._owner = owner

        # These are the base concepts for the relation concept set
        self._elements = set()
        self._partial = set()

        # Derivied elements
        self._derivedElements = set()
        self._derivedPartial = collections.defaultdict(int)

        # Add in the concepts from the iterable
        for concept in iterable: self.add(concept)

    def __len__(self): return len(self._derivedElements)
    def __iter__(self): return iter(self._derivedElements)
    def __contains__(self, concept: Concept): return concept in self._derivedElements

    def add(self, concept: Concept) -> None:
        """ Add a concept as a base relation concept which shall mean that all descendants of this concept are valid
        group members. Partials can be added for placeholder (str)

        Params:
            concept (Concept/str): the concept to be added
        """

        if isinstance(concept, str):
            # Partial base being added
            if concept in self._elements:
                # The concept is already expressed
                return

            # Add the partial concept into the bases and into the derived collection
            super().add(concept)
            self._derivedElements.add(concept)
            self._derivedPartial[concept] += 1

            return

        # Adding a concept to the concept set, ensuring that it isn't already expressed
        if (
            (concept in self._elements and concept not in self._partial) or
            (concept.ancestors().intersection(self._elements))
        ):
            log.warning("Concept {} was already expressed by relation concept set".format(concept))
            return

        # Add the concept into the bases set and the derived group
        super().add(concept)
        self._add(concept)

    def _add(self, concept: Concept):
        """ Only add the concept in to the derive elements if not already present

        """

        queryGroup = [concept]

        while queryGroup:
            query = queryGroup.pop()

            if isinstance(query, str):
                self._derivedElements.add(query)
                self._derivedPartial[query] += 1

            else:
                if query not in self._derivedElements:
                    self._derivedElements.add(query)
                    query._relationMembership[self._owner] = query._relationMembership.get(self._owner, 0) + 1

                    queryGroup += list(query.children)

    def _subscribe(self, concept: Concept):

        #! Partial concepts that are added as children to concepts shall not inherit of become part of this concept

        if concept not in self._derivedElements and concept.ancestors().intersection(self._elements):
            self._add(concept)

    def discard(self, concept: Concept):
        """

        """
        if concept not in self._elements: return False  # Not present
        if concept in self._partial: return super().discard(concept)  # Only partial - remove and return

        # If full concept as member by partial passed - convert partial to full concept
        if isinstance(concept, str): concept = self._elements.intersection({concept}).pop()

        # remove the concept and delink it
        super().discard(concept)
        self._delink(concept)
        return self._discard(list(concept.children))

    def _unsubscribe(self, concept: Concept):

        if concept not in self._derivedElements: return

        if isinstance(concept, str):
            return self._decrementDerivedPartial(concept)
        self._discard([concept])

    def _discard(self, concepts: [Concept]):

        while concepts:
            concept = concepts.pop()

            if isinstance(concept, str): self._decrementDerivedPartial(concept)

            elif not concept.ancestors().intersection(self._elements):

                self._derivedElements.discard(concept)
                self._delink(concept)
                concept._relationMembership[self._owner] = concept._relationMembership.get(self._owner, 1) - 1
                if concept._relationMembership[self._owner] == 0: del concept._relationMembership[self._owner]

                concepts += list(concept.children)

        return True

    def _delink(self, concept: Concept):
        concept._relationMembership[self._owner] -= 1
        if concept._relationMembership[self._owner] == 0:
            del concept._relationMembership[self._owner]

    def _decrementDerivedPartial(self, partial: str):
        """

        """
        # Decrement the existence of the partial child
        self._derivedPartial[partial] -= 1

        if not self._derivedPartial[partial]:
            # There is no more supporting parent concepts - remove the partial
            self._derivedElements.discard(partial)
            del self._derivedPartial[partial]






class RelationConceptManager(collections.abc.MutableSequence):
    """ Manage a collection of RelationConceptSets whose order matters. The index of a RelationConceptSet relates to
    another RelationConceptSet stored in another RelationConceptSet, it indicated what concepts out of the pairs can
    hold this relationship between them

    Params:
        owner (Relation): The relation object that this Manager belongs too
        isDomain (bool): Indicates whether or not this manager is managing the domains or targets for the relation
    """

    def __init__(self, owner: Relation, concepts: list, isDomain: bool = True):

        self._owner = owner
        self._elements = []
        self._isDomain = isDomain

        if len(concepts):
            # Generically extract the first item from the concepts
            firstItem = next(iter(concepts))

            if isinstance(firstItem, (Vertex, str)):
                # The input in a single iterable of concepts
                self._elements.append(RelationConceptSet(self._owner, concepts))

            else:
                # The inputs is a list of concept iterables
                for group in concepts:
                    self._elements.append(RelationConceptSet(self._owner, group))

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __getitem__(self, index: int): return self._elements[index]
    def __setitem__(self, index: int, item: ConceptSet):
        if isinstance(item, ConceptSet):
            self._elements[index].empty()
            for concept in item:
                self._elements[item].add(concept)
    def __delitem__(self, index: int):
        # Delete from both group the references to the concept sets
        del self._elements[index]
        del self._correspondingGroup()._elements[index]

    def __contains__(self, concept: Concept): return any(concept in group for group in self._elements)
    def __call__(self): return {concept for conceptset in self._elements for concept in conceptset}

    def insert(self, index: int, concepts: ConceptSet):
        self._elements.insert(index, RelationConceptSet(self._owner, concepts))
        self._correspondingGroup()._elements.insert(index, RelationConceptSet(self._owner, []))

    def append(self, concepts: ConceptSet):

        self._elements.append(RelationConceptSet(self._owner, concepts))
        self._correspondingGroup()._elements.append(RelationConceptSet(self._owner, []))

        return len(self) - 1  # Index of newly added conceptset

    def add(self, concept: Concept, group: int = None):

        if group:
            self._elements[group].add(concept)
            return

        for group in self._elements:
            group.add(concept)

    def _correspondingGroup(self): return self._owner.targets if self._isDomain else self._owner.domains

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