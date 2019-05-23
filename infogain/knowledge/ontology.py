import os
import collections
import weakref

from ..exceptions import MissingConcept
from .concept import Concept
from .relation import Relation
from .rule import Rule, Condition

import logging
log = logging.getLogger(__name__)

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
        self._concepts = OntologyConcepts(weakref.proxy(self))
        self._relations = OntologyRelations(weakref.proxy(self))

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

    @property
    def concepts(self):
        """ MutableMapping Object for ontology concepts """
        return self._concepts

    @property
    def relations(self):
        """ MutableMapping object for ontology relations """
        return self._relations

    def findRelations(self, domain: str, target: str) -> [Relation]:
        """ Return a list of relations that could be formed between the domain and the target
        objects. Yield the relations.

        Params:
            domain (str) - A concept that needs to match with the domain of potential relations
            target (str) - A concept that needs to match with the target of potential relations
        """

        dom = self.concepts(domain) if isinstance(domain, str) else domain
        tar = self.concepts(target) if isinstance(target, str) else target
        if None in (dom, tar):
            raise Exception("Invalid concepts provided when looking for relations")

        for relation in self._relations.values():
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

class OntologyConcepts(collections.abc.MutableMapping):
    """ The container of member concepts of an ontology. Provides the interface to add, edit, and remove concepts from
    the ontology

    Params:
        owner (Ontology): The ontology that this container belongs to
    """

    def __init__(self, owner: Ontology):
        self._owner = owner
        self._elements = {}

        self._missedConcepts = collections.defaultdict(set)   # Mapping between incomplete concepts
        self._missedRelations = collections.defaultdict(set)  # Mapping between incomplete concepts and relations

    def __getitem__(self, name: str) -> Concept: return self._elements[name]
    def __setitem__(self, name: str, concept: Concept) -> None: self._elements[name] = concept
    def __delitem__(self, name: str) -> None:
        """ Remove the concept from the ontology. Remove the concept from every relation/rule where applicable """
        del self._elements[name]
    def __iter__(self): return iter(self._elements)
    def __len__(self): return len(self._elements)
    def __call__(self, name: str = None) -> Concept:
        """ Return the ontology concepts, or, the concept given by the name parameter

        Params:
            name (str) = None: If provided, return the concept with the given name, else all concepts
        """
        if name is not None: return self.get(name)
        return set(self._elements.values())

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
                found = self[step]
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
        if concept.name in self._missedRelations:
            for relation in self._missedRelations[concept.name]:
                relation.subscribe(concept)

        self[concept.name] = concept

    def remove(self, concept: Concept) -> None:
        del self[concept.name]

class OntologyRelations(collections.abc.MutableMapping):

    def __init__(self, owner: Ontology):
        self._owner = owner
        self._elements = {}

    def __getitem__(self, name: str) -> Relation: return self._elements[name]
    def __setitem__(self, name: str, relation: Relation) -> None: self._elements[name] = relation
    def __delitem__(self, name: str) -> None:
        del self._elements[name]
    def __iter__(self): return iter(self._elements)
    def __len__(self): return len(self._elements)
    def __call__(self, name: str = None) -> Relation:
        if name is not None: return self.get(name)
        return set(self._elements.values())

    def add(self, relation: Relation) -> Relation:
        """ Add a new relation object to the ontology, correctly link the relation concepts to the
        ontology.

        Params:
            relation (Relation) - The relation object to add to the ontology

        Returns:
            Relation - The original relation or a newly generated relation with edits.
        """

        # Resolve any partial concepts that exist within the relation - record missed concepts
        for partial in relation.concepts.partials():
            found = self._owner.concepts(partial)
            if found:
                relation.subscribe(found)
            else:
                self._owner.concepts._missedRelations[partial].add(relation)

        log.debug("Added Relation {}".format(str(relation)))
        self[relation.name] = relation
        return relation