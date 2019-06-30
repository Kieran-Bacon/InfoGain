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
        self._domains = RuleConceptSet(self, domains, isDomain=True)
        self._targets = RuleConceptSet(self, targets, isDomain=False)

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
        self._subscribe(concept)

    def _subscribe(self, concept: Concept) -> None:
        self.domains._subscribe(concept)
        self.targets._subscribe(concept)

    def _unsubscribe(self, concept: Concept) -> None:
        self.domains._unsubscribe(concept)
        self.targets._unsubscribe(concept)

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

    def clone(self):
        """ Generate a deep copy of this Rule - All references to concepts are replaced with strings

        Returns:
            Rule: A new Rule emblematic of the original
        """
        return Rule(
            self.domains.bases.toStringSet(),
            self.targets.bases.toStringSet(),
            self.confidence,
            supporting=self.supporting,
            conditions=[condition.clone() for condition in self._conditions]
        )

class RuleConceptSet(ConceptSet):

    def __init__(self, owner: Rule, iterable: {Concept} = set(), isDomain: bool = True):

        self._owner = owner
        self._isDomain = isDomain

        self._bases = set()
        super().__init__(self)  # Initialise the internal variables of the concept set

        if isinstance(iterable, (str, Concept, Instance)):
            self.add(iterable)
        else:
            for con in iterable: self.add(con)

    @property
    def bases(self): return self._bases.copy()

    def add(self, concept: Concept):
        """ Add a concept to the rule set

        Params:
            concept (Concept): Works

        """

        #TODO: Ensure that the base isn't expressed by bases of the rule already - paying attention to domain/target

        self._bases.add(concept)
        super().add(concept)

        if not isinstance(concept, str):
            if self._isDomain:
                for child in concept.descendants(): super().add(child)
            else:
                for parent in concept.ancestors(): super().add(parent)

                if self._owner.conditions.isConditionOnTarget():
                    for child in concept.descendants(): super().add(child)

    def discard(self, concept: Concept):

        if concept not in self._bases: return

        self._bases.remove(concept)
        super().discard(concept)

        # For children of the bases, check whether they should also be discarded
        isDiscard = list(concept.children)

        while isDiscard:
            concept = isDiscard.pop()

            if not concept.ancestors().intersection(self._bases):
                # Concept not expressed - remove and add its children for checking
                super().discard(concept)
                isDiscard += list(concept.children)

    def _subscribe(self, concept: Concept, cascade: bool = True):

        # Check with the concept is already expressed
        if isinstance(concept, str) and concept in self._elements: return
        if concept not in self._partial and concept in self._elements: return

        if self._isDomain:
            # We are the Rule's domains so all descendants of this Concept are applicable
            if concept.ancestors().intersection(self._bases):
                super().add(concept)

                if cascade:
                    for child in concept.descendants(): self._subscribe(child, cascade = False)

        else:

            cascadeUp = bool(concept.descendants().intersection(self._bases))
            cascadeDown = self._owner.conditions.isConditionOnTarget() and concept.ancestors().intersection(self.bases)

            if cascadeUp or cascadeDown:
                super().add(concept)

                if cascade:
                    if cascadeUp:
                        for parent in concept.ancestors(): self._subscribe(parent, False)

                    if cascadeDown:
                        for child in concept.descendants(): self._subscribe(child, False)


    def _unsubscribe(self, concept: Concept):
        #TODO
        pass

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