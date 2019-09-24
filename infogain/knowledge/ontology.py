import os
import collections
import weakref

from ..exceptions import MissingConcept
from .concept import Concept
from .relation import Relation
from .rule import Rule, Condition

import logging
log = logging.getLogger(__name__)

class OntologyConcepts(collections.abc.MutableMapping):
    """ The container of member concepts of an ontology. Provides the interface to add, edit, and remove concepts from
    the ontology

    Params:
        owner (Ontology): The ontology that this container belongs to
    """

    def __init__(self, owner: weakref.ref):
        self._ownerRef = owner
        self._elements = {}

        self._missedConcepts = collections.defaultdict(set)   # Mapping between incomplete concepts
        self._missedSubscriptions = collections.defaultdict(set) # Mapping between partial concepts and components

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __getitem__(self, name: str) -> Concept: return self._elements[name]
    def __setitem__(self, name: str, concept: Concept) -> None: self.add(concept)
    def __delitem__(self, name: str) -> None: self.remove(self._elements[name])
    def __call__(self) -> Concept: return set(self._elements.values())

    @property
    def _owner(self): return self._ownerRef()

    def add(self, concept: Concept) -> None:
        """ Add concept object to ontology, overwrite previous concept if present.
        Identifies the relation ships concepts parent objects are and becomes members to those
        relations if applicable.

        Params:
            concept (Concept) - The concept to add
        """

        # Record all partial links between this concept and external concepts
        for family in [concept.parents, concept.children]:
            for step in family.partials():
                found = self.get(step)
                if found:
                    family.add(found)  # Family member found, add to concept and connect (internally)
                else:
                    self._missedConcepts[step].add(concept)  # Record that concept is looking for this family member

        # Link wth concept with any concepts that reference this newly added concept partially
        if concept.name in self._missedConcepts:
            for family in self._missedConcepts[concept.name]:
                # Determine what the relationship between the two concepts is by checking partial membership
                if concept in family.parents: family.parents.add(concept)
                elif concept in family.children: family.children.add(concept)
            del self._missedConcepts[concept.name]

        # Link with any relations that have a reference to this concept partially and require the full concept
        if concept.name in self._missedSubscriptions:
            for component in self._missedSubscriptions[concept.name]:
                component._subscribe(concept)

        self._elements[concept.name] = concept

    def remove(self, concept: Concept) -> None:
        raise NotImplementedError()

class OntologyRelations(collections.abc.MutableMapping):

    def __init__(self, owner: weakref.ref):
        self._ownerRef = owner
        self._elements = {}

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __getitem__(self, name: str) -> Relation: return self._elements[name]
    def __setitem__(self, name: str, relation: Relation) -> None: self._elements[name] = relation
    def __delitem__(self, name: str) -> None: self.remove(self._elements[name])
    def __call__(self, name: str = None) -> Relation: return set(self._elements.values())

    @property
    def _owner(self): return self._ownerRef()

    def add(self, relation: Relation) -> Relation:
        """ Add a new relation object to the ontology, correctly link the relation concepts to the
        ontology.

        Params:
            relation (Relation) - The relation object to add to the ontology

        Returns:
            Relation - The original relation or a newly generated relation with edits.
        """

        for rule in relation.rules:
            for partial in {p for g in (rule.domains, rule.targets) for p in g.partials()}:
                found = self._owner.concepts.get(partial)
                if found:
                    rule._subscribe(found)
                else:
                    self._owner.concepts._missedSubscriptions[partial].add(rule)

        # Resolve any partial concepts that exist within the relation - record missed concepts
        for partial in {p for c in (relation.domains, relation.targets) for g in c for p in g.partials()}:

            found = self._owner.concepts.get(partial)
            if found:
                relation._subscribe(found)
            else:
                self._owner.concepts._missedSubscriptions[partial].add(relation)

        log.debug("Added Relation {}".format(str(relation)))
        self[relation.name] = relation
        return relation

    def remove(self, relation: Relation):
        raise NotImplementedError()

class Ontology:
    """ An ontology is a collection of knowledge, it contains a collection of concepts
    and the relationships between them.

    Args:
        name (str): The name given to the ontology
        filepath (str): The location of a saved ontology to expand
    """

    def __init__(self, name: str = None):

        # Simply identification of the ontology, no functional use
        self.name = name

        # The internal storage containers
        self._concepts = OntologyConcepts(weakref.ref(self))
        self._relations = OntologyRelations(weakref.ref(self))

    @property
    def concepts(self) -> OntologyConcepts: return self._concepts
    @property
    def relations(self) -> OntologyRelations: return self._relations


    def importBuiltin(self, module_name: str) -> None:
        """ Import knowledge considered common (and required) in most applications. Add the

        Params:
            module_name (str): The builtin title
        """
        import importlib

        try:
            module = importlib.import_module("infogain.knowledge.builtin_concepts.collection_{}".format(module_name))
            [self.concepts.add(con) for con in module.concepts()]
        except ImportError:
            msg = "ImportError - No builtin module by that name: {}".format(module_name)
            log.error(msg, exc_info=True)
            raise ImportError(msg)

    def findRelations(self, domain: str, target: str) -> [Relation]:
        """ Return a list of relations that could be formed between the domain and the target
        objects. Yield the relations.

        Params:
            domain (str) - A concept that needs to match with the domain of potential relations
            target (str) - A concept that needs to match with the target of potential relations
        """

        dom = self.concepts.get(domain) if isinstance(domain, str) else domain
        tar = self.concepts.get(target) if isinstance(target, str) else target
        if None in (dom, tar):
            raise Exception("Invalid concepts provided when looking for relations")

        for relation in self.relations():
            if relation.between(dom, tar):
                yield relation

    def clone(self):
        """ Create a new ontology object that is a deep copy of this ontology instance

        Returns:
            clone (Ontology) - A deep copy of this ontology object
        """

        # Create a new ontology object with the same name
        ontologyClone = Ontology(self.name)

        # Clone each item in the ontology and add the cloned item into the ontology clone
        for concept in self.concepts(): ontologyClone.concepts.add(concept.clone())
        for relation in self.relations(): ontologyClone.relations.add(relation.clone())

        # return the cloned ontology
        return ontologyClone