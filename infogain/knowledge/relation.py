import weakref
import collections
import typing

from ..exceptions import MissingConcept
from ..information import Vertex
from .concept import Concept, ConceptSet
from .instance import Instance
from .rule import Rule

import logging
log = logging.getLogger(__name__)


class RelationConceptSet(ConceptSet):
    """ Holds a set of concepts has the/a relation to another set of concepts for the Relation. Handle consistency of
    concepts set by updating via subscription on concept hierachy changes

    Params:
        owner (weakref.ref): Owning Relation object
        iterable (typing.Iterable[Concept]): Initial seed of concepts for set
    """

    def __init__(self, owner: weakref.ref, iterable: typing.Iterable[Concept]):

        self._ownerRef = owner

        # These are the base concepts for the relation concept set
        self._elements = set()
        self._partial = set()

        # Derivied elements
        self._derivedElements = set()
        self._derivedPartial = collections.defaultdict(int)

        # Add in the concepts from the iterable
        for concept in iterable: self.add(concept)

    @property
    def _owner(self): return self._ownerRef()
    @property
    def bases(self) -> ConceptSet: return ConceptSet(self._elements)

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

    def _add(self, concept: Concept) -> None:
        """ Add a concept into the Set, but, don't record the concept as a base. Non base concepts must be expressed by
        a base concept. Being a none base concept shall mean that the concept is removed when all expressing concepts
        are removed.

        Params:
            concept (Concept):
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
        """ Add the concept into the concept set if it is expressed by another concept

        Params:
            concept (Concept)
        """

        #! Partial concepts that are added as children to concepts shall not inherit of become part of this concept

        if concept in self._partial:
            # A base partial concept being replaced - Remove the partial concept from everywhere

            super().discard(concept)
            del self._derivedPartial[concept.name]
            self._derivedElements.remove(concept)

            return self.add(concept)

        if concept in self._derivedPartial:
            # A derived partial concept - remove partial and add derived concept

            del self._derivedPartial[concept.name]
            self._derivedElements.remove(concept)

            return self._add(concept)

        if concept not in self._derivedElements and concept.ancestors().intersection(self._elements):
            self._add(concept)

    def discard(self, concept: Concept) -> bool:
        """ Remove a concept from the concept set if it is present

        Params:
            concept (Concept)

        Returns:
            bool: True if the concept was removed
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
        """ Re-evaluate a concepts membership. Remove concept if they are unexpressed

        Params:
            concept (Concept)
        """

        if concept not in self._derivedElements: return

        if isinstance(concept, str):
            return self._decrementDerivedPartial(concept)
        self._discard([concept])

    def _discard(self, concepts: typing.Iterable[Concept]):
        """ Discard a number of concepts performing all consistency actions in the interim

        Params:
            concepts (typing.Iterable[Concept]): An iterable of concepts to be discarded
        """

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
        """ Remove the concepts reference to the relation as the relation no longer applies/uses this concept

        Params:
            concept (Concept): the concept to remove connection/link from
        """

        concept._relationMembership[self._owner] -= 1
        if concept._relationMembership[self._owner] == 0:
            del concept._relationMembership[self._owner]

    def _decrementDerivedPartial(self, partial: str):
        """ Decrement a partial concept's counter, removing it entirely if the counter becomes 0

        Params:
            partial (str): partial name
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

    def __init__(self, owner: weakref.ref, concepts: list, isDomain: bool = True):

        self._ownerRef = owner
        self._elements = []
        self._isDomain = isDomain

        if len(concepts):
            # Generically extract the first item from the concepts
            firstItem = next(iter(concepts))

            if isinstance(firstItem, (Vertex, str)):
                # The input in a single iterable of concepts
                self._elements.append(RelationConceptSet(owner, concepts))

            else:
                # The inputs is a list of concept iterables
                for group in concepts:
                    self._elements.append(RelationConceptSet(owner, group))

    @property
    def _owner(self): return self._ownerRef()

    def __repr__(self): return "<RelationConceptGroups[{}]>".format(",".join(self._elements))
    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __getitem__(self, index: int): return self._elements[index]
    def __setitem__(self, index: int, conceptSet: typing.Iterable[Concept]):
        self._elements[index].clear()
        for concept in conceptSet:
            self._elements[index].add(concept)
    def __delitem__(self, index: int):
        # Delete from both group the references to the concept sets
        del self._elements[index]
        del self._correspondingGroup()._elements[index]

    def __contains__(self, concept: Concept): return any(concept in group for group in self._elements)
    def __call__(self): return {concept for conceptset in self._elements for concept in conceptset}

    def insert(self, index: int, concepts: ConceptSet):
        """ Insert into ConceptSet Manager a new source ConceptSet. Ensure that the corresponding Manager inserts a
        new source set at the same location to keep consistency

        Params:
            index (int):
            concepts (ConceptSet): The source concept set
        """
        self._elements.insert(index, RelationConceptSet(self._ownerRef, concepts))
        self._correspondingGroup()._elements.insert(index, RelationConceptSet(self._ownerRef, []))

    def append(self, concepts: ConceptSet):
        """ Add a source ConceptSet to the manager, trigger the appending of an empty set to the corresponding manager

        Params:
            concepts (ConceptSet): the set of concepts to act as a source
        """

        self._elements.append(RelationConceptSet(self._ownerRef, concepts))
        self._correspondingGroup()._elements.append(RelationConceptSet(self._ownerRef, []))

        return len(self) - 1  # Index of newly added conceptset

    def add(self, concept: Concept, group: int = None):
        """ Add a concept to the managers sources. If a source/group is selected, add specifically to that group

        Params:
            concept (Concept): The concept to add
            group (int) = None: index of the group to add the concept to, all if None
        """

        if group:
            return self._elements[group].add(concept)

        for group in self._elements:
            group.add(concept)

    def _correspondingGroup(self):
        """ Using the owner - return the corresponding manager object of the relation (domain <-> target) """
        return self._owner.targets if self._isDomain else self._owner.domains

class RuleManager(collections.abc.Sequence):
    """ Rule Manager which orders and maintains the rules that provide confidence for the relation.

    Params:
        owner (weakref.ref): Owning Relation
        rules (typing.Iterable[Rule]): seed iterable of rules
    """

    def __init__(self, owner: weakref.ref, rules: typing.Iterable[Rule] = []):
        self._ownerRef = owner
        self._elements = rules.copy()

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __getitem__(self, index: int): return self._elements[index]
    def __delitem__(self, index: int): self.remove(self._elements[index])
    def __contains__(self, rule: Rule): return rule in self._elements
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

    @property
    def _owner(self): return self._ownerRef()

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

    def remove(self, rule: Rule) -> None: self._elements.remove(rule)

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
        self._domains = RelationConceptManager(weakref.ref(self), domains, isDomain = True)
        self._targets = RelationConceptManager(weakref.ref(self), targets, isDomain = False)
        assert len(self._domains) == len(self._targets), "Inconsistent types of domains and targets passed"
        self.rules = rules
        self.differ = differ

    @property
    def domains(self) -> RelationConceptManager: return self._domains
    @property
    def targets(self) -> RelationConceptManager: return self._targets
    @property
    def rules(self) -> RuleManager: return self._rules
    @rules.setter
    def rules(self, rules: [Rule]): self._rules = RuleManager(weakref.ref(self), rules)

    def __repr__(self):
        return "<Relation {}: {} - {}>".format(self.name, self._domains, self._targets)

    def __str__(self):
        return " ".join([str({str(x) for x in self._domains}), self.name, str({str(x) for x in self._targets})])

    def appendConceptSets(self, domains: ConceptSet, targets: ConceptSet) -> int:
        """ Append a concept set mapping from specified domains to specified targets

        Params:
            domains (ConceptSet): The collection of domain concepts
            targets (ConceptSet): The collection of target concepts

        Returns:
            int: The index of concept sets
        """
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
            if ancestors.intersection(domains) or concept in domains.partials(): domains._subscribe(concept)
            if ancestors.intersection(targets) or concept in targets.partials(): targets._subscribe(concept)

        # For each of the rules, pass the concept on as relevant
        for rule in self._rules: rule._subscribe(concept)

    def _unsubscribe(self, concept: Concept):
        """ Check whether a concept should still be a member, ensure that it is removed if it is present and it should
        no longer be a member

        Params:
            concept (Concept)
        """

        # Collect the ancestors of this concept
        ancestors = concept.ancestors()

        # For all the concept sets check whether they are
        for domains, targets in zip(self.domains, self.targets):
            if concept in domains and not ancestors.intersection(domains): domains._unsubscribe(concept)
            if concept in targets and not ancestors.intersection(targets): targets._unsubscribe(concept)

        for rule in self._rules: rule._unsubscribe(concept)

    def clone(self):
        return Relation(
            [domain.bases.toStringSet() for domain in self.domains],
            self.name,
            [target.bases.toStringSet() for target in self.targets],
            [rule.clone() for rule in self._rules],
            self.differ
        )