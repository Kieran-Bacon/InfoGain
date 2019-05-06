import collections

from .concept import Concept, ConceptSet
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

        # Create the domains and target sets
        self._conditions = ConditionManager(self)
        self._domains = RuleConceptSet(self, domains, domains=True)
        self._targets = RuleConceptSet(self, targets, domains=False)

        self.confidence = confidence
        self.supporting = supporting

        for condition in conditions: self._conditions.add(condition)

    def __repr__(self):
        confidence = self.confidence if self.supporting else self.confidence*-1
        base = "<Rule: {} {} is true with {}".format(self.domains, self.targets, confidence)
        if self._conditions:
            base += " when:\n"
            base += "\n".join([str(condition) for condition in self._conditions])

        return base

    @property
    def domains(self): return self._domains
    @property
    def targets(self): return self._targets
    @property
    def conditions(self): return self._conditions

    def subscribe(self, concept: Concept) -> None:
        self.domains.subscribe(concept)
        self.targets.subscribe(concept)

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

        # Ensure that the arguments are comparable
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

    def minimise(self) -> dict:
        """ Reduce the rule down to a dictionary object that defines the rule

        Returns:
            dict: keys {"domains", "targets", "confidence", "supporting", "conditions"}
        """

        minimised = {
            "domains": sorted(self.domains.bases.toStringSet()),
            "targets": sorted(self.targets.bases.toStringSet()),
            "confidence": self.confidence
        }

        if self.conditions:
            minimised["conditions"] = [condition.minimise() for condition in self.conditions]
        if not self.supporting: minimised["supporting"] = self.supporting

        return minimised

    def clone(self):
        """ Generate a deep copy of this Rule - All references to concepts are replaced with strings

        Returns:
            Rule: A new Rule emblematic of the original
        """
        return Rule(
            self.domains.bases,
            self.targets.bases,
            self.confidence,
            supporting=self.supporting,
            conditions=[condition.clone() for condition in self._conditions]
        )

class RuleConceptSet(collections.abc.MutableSet):

    def __init__(self, owner: Rule, iterable: {Concept} = set(), domains: bool = True):
        self._owner = owner

        self._base = set()
        self._elements = set()
        self._partial = set()

        self._isDomain = domains

        if isinstance(iterable, (str, Concept, Instance)):
            self.add(iterable)
        else:
            for con in iterable: self.add(con)

    def __len__(self): return len(self._elements)
    def __bool__(self): return bool(self._base)
    def __iter__(self): return iter(self._elements)
    def __contains__(self, concept: Concept): return concept in self._elements

    def __repr__(self): return "<RuleConceptSet{}>".format(self._elements)

    @property
    def bases(self): return ConceptSet(self._base)

    def add(self, concept: Concept) -> None:
        """

        """
        return self._add(concept, True)
    def _add(self, concept: Concept, base: bool = False) -> None:

        if isinstance(concept, str):
            if concept in self._elements: return  # Cannot add a partial if its already in elements
            self._partial.add(concept)  # Record that this added concept is only partial
        elif concept in self._partial:
            # This is a non partial element to replace the current partial element
            if base: self._base.remove(concept)
            self._elements.remove(concept)  # Remove the partial element
            self._partial.remove(concept)  # Remove the partial tag

        # Add the element into the set
        if base: self._base.add(concept)
        self._elements.add(concept)
        if isinstance(concept, str): return

        if base:
            # If the Rule has conditions, we need to cascade this set of concepts
            if self._isDomain:
                # We are the Rule's domains so all descendants of this Concept are applicable
                for dom in concept.descendants(): self._add(dom)
            else:
                # We are the Rule's targets so all ancestors of this concept are applicable
                for tar in concept.ancestors(): self._add(tar)

                # The Rule is conditional on the target, include target descendants
                if self._owner.conditions.isConditionOnTarget():
                    for tar in concept.descendants(): self._add(tar)

    def discard(self, concept: Concept) -> None:

        if concept not in self._base: return

        self._base.remove(concept)
        self.minimise()

    def subscribe(self, concept: Concept) -> None:
        if self._isDomain:
            # We are the Rule's domains so all descendants of this Concept are applicable
            if concept.ancestors().intersection(self._base):
                self._add(concept)
        else:
            # We are the Rule's targets so all ancestors of this concept are applicable
            if (concept.descendants().intersection(self._base) or
                (self._owner.conditions.isConditionOnTarget() and
                concept.ancestors().intersection(self._base))
                ):
                self._add(concept)

    def expand(self):
        """ We are to expand the set to include required concepts given that the conditions are present"""

        if self._isDomain:

            # For each of the children of the base domains, add them in
            for concept in self._base:
                if isinstance(concept, str): continue
                for child in concept.descendants():
                    self._add(child)

        else:

            # For each of the children of the base domains, add them in
            for concept in self._base:
                if isinstance(concept, str): continue
                for parent in concept.ancestors():
                    self._add(parent)


            if self._owner.conditions.isConditionOnTarget():
                for concept in self._base:
                    if isinstance(concept, str): continue
                    for child in concept.descendants():
                        self._add(child)

    def minimise(self):
        """ Reduce the rule to its minimum. If there are still conditions that shall expand concepts then it shall bloat
        back to its enlarged size
        """

        base = self._base
        self._base = set()
        self._elements = set()
        self._partial = set()

        for concept in base:
            self._add(concept, True)

    def partials(self) -> {str}:
        """ Provide a set of the partial concepts within the set

        Returns:
            {str}: A set of concept names yet to be linked correctly
        """
        return self._partial.copy()

class ConditionManager(collections.abc.MutableSequence):
    """ A list like object that houses Condition objects while providing useful convenient methods for interacting with
    them

    Params:

    """

    def __init__(self, owner: Rule):
        self._owner = owner
        self._elements = []

        self._isConditionOnTargets = False

    def __bool__(self): return bool(self._elements)
    def __iter__(self): return iter(self._elements)
    def __len__(self): return len(self._elements)
    def __getitem__(self, index: int): return self._elements[index]
    def __setitem__(self, index: int, condition: Condition): self.add(condition)
    def __delitem__(self, index: int): self.remove(self[index])
    def insert(self, index: int, condition: Condition): self.add(condition)

    def add(self, condition: Condition) -> None:
        """ Add a condition object into this condition Manager, order the conditions relative to its salience

        Params:
            condition (Condition): the condition to add
        """

        i = 0  # Assign 0 in case the elements list is empty
        for i, cond in enumerate(self._elements):
            if condition.salience >= cond.salience: break
        else:
            i += 1
        self._elements.insert(i, condition)  # Insert the rule into the collection

        # If the condition is conditional on the target, expand the targets to include descendants
        if condition.containsTarget() and not self._isConditionOnTargets:
            self._isConditionOnTargets = True
            self._owner.targets.expand()

    def remove(self, condition: Condition) -> None:
        """ Remove a condition object from this Condition Manager and subsequently the Rule

        Params:
            condition (Condition): the condition object to remove
        """
        self._elements.remove(condition)

        # If we have just the last condition that contains the target, minimise the targets
        if (self._isConditionOnTargets and
            condition.containsTarget() and
            not any((condition.containsTarget() in self._elements))):

            self._isConditionOnTargets = False
            self._owner.targets.minimise()

    def isConditionOnTarget(self):
        return self._isConditionOnTargets