import uuid
from collections.abc import MutableSet

from ..information import Vertex
from .instance import Instance
from ..exceptions import ConsistencyError

import logging
log = logging.getLogger(__name__)

# class ConceptSet(MutableSet):

#     def __init__(self, iterable: {Concept} = None):
#         for con in iterable: self.add(con)
#         self._partial = set()

#     def expand(self, descending: bool = True) -> None:
#         """ Expand a collection of concepts to include either their descendants or their ancestors when applicable

#         Params:
#             descending (bool): Dictate the direction of expansion
#         """

#         expansion = set()

#         for concept in self:
#             expansion.add(concept)
#             if isinstance(concept, Concept):
#                 group = concept.descendants() if descending else concept.ancestors()
#                 for con in group:
#                     if isinstance(con, str) or con.category is not Concept.ABSTRACT:
#                         expansion.add(con)

#         for concept in expansion: self.add(concept)

#     def minimise(self, ascending: bool = True) -> None:
#         """ Minimise a collection according to possible concepts within another.

#         Params:
#             collection (set): The collection that is being minimised
#         """
#         minimised = set()

#         for con in self:
#             if isinstance(con, Concept):
#                 group = con.ancestors() if ascending else con.descendants()
#                 if group.intersection(self): continue

#             minimised.add(con)

#         for c in self: self.remove(c)
#         for c in minimised: self.add(c)

#     def toStringSet(self):
#         """ Generate a conventional set of concept names (str) from this concept set and return

#         Returns:
#             {str}: A set of concept names which are strings
#         """
#         return {c if isinstance(c, str) else c.name for c in self}

class FamilyConceptSet(MutableSet):
    """ A set to hold information of a family hierarchy. Concepts held in this set are the parents or children of the
    concept that holds this set. The set is responsible for making consisten this relationship with the concepts in this
    set.

    Params:
        iterable ({Concept}): A collection of concepts to act as the initial members of the set
        ancestors (bool): Indicates whether this set holds the the parents or children of the class
    """

    def __init__(self, owner: Vertex = None, ancestors: bool = True):
        self._elements = set()
        self._owner = owner
        self._ancestors = ancestors
        self._partial = set()

    def __iter__(self): return iter(self._elements)
    def __len__(self): return len(self._elements)
    def __contains__(self, x): return x in self._elements

    def isAncestors(self): return self._ancestors

    def add(self, concept: Vertex) -> None:
        """ Add a concept into this set. If the concept is partial, store its information such that it can be replaced
        at a later date. If this is the parent set, pull down relations that have been set up on the concepts within.

        Params:
            concept (Concept): The concept to be added into the set
        """
        if isinstance(concept, str):
            self._elements.add(concept)
            self._partial.add(concept)  # The concept is added, but it is also simply a partial concept
            return

        if concept in self._partial:
            # This is a non partial element to replace the current partial element
            self._elements.remove(concept)
            self._partial.remove(concept)

        # Add the concept into this FamilyConceptSet
        self._elements.add(concept)

        # Identify corresponding family concept set from new concept + pull down relations where applicable
        if self._ancestors:
            # Pull down relations from the new parent concept
            for relation in concept._relationMembership:
                self._owner._relationMembership.add(relation)
                relation.subscribe(self._owner)

            otherSet = concept.children

        else:
            otherSet = concept.parents

        # Check whether the owning concept is correctly linked with the new concept from their perspective
        if not otherSet.linked(self._owner):
            otherSet.add(self._owner)

    def discard(self, concept: Vertex) -> None:
        """ Removing a concept from the family set shall remove the it and all of its does """
        if concept in self._partial: self._partial.remove(concept)
        if concept in self._elements: self._elements.remove(concept)

    def linked(self, concept: Vertex):
        """ Determine whether this concept is correctly linked inside this concept set. Linked if the concept is within
        the set and isn't partial.

        Params:
            concept (Concept): The concept that is being checked if correctly a member
        """
        return concept not in self._partial and concept in self._elements

    def partials(self):
        """ Provide a set of the partial concepts within the set """
        return self._partial.copy()

    def copy(self): return self._elements.copy()

class Concept(Vertex):
    """ A concept represents a "thing", an idea, an object, a place, anything.

    Args:
        name (str): The name/representation for the concept
        parents (set): A set of concepts/strings that represent parent concepts
        children (set): A set of concepts/strings that represent child concepts
        alias (set(str)): A set of string representations for the concept that maybe found in text
        properties (dict): A property of a concept e.g "age": 20
        category ("abstract"/"static"/"dynamic"): The class of the concept - defines behaviour
        json (dict): The concept information in the form of a diction, expected from json
    """

    ABSTRACT = "abstract"
    STATIC = "static"
    DYNAMIC = "dynamic"

    def __init__(self,
        name: str,
        parents: set = set(),
        children: set = set(),
        alias: set = set(),
        properties: dict = {},
        category: str = "dynamic",
        json: dict = {}
        ):

        self.name = name

        # Relationships this concept is a part of
        self._relationMembership = set()

        # Family hierarchy structures
        self.parents = FamilyConceptSet(owner=self, ancestors=True)
        self.children = FamilyConceptSet(owner=self, ancestors=False)
        for con in parents: self.parents.add(con)
        for con in children: self.children.add(con)

        # Concept aliases and properties
        self.alias = alias
        self.properties = properties.copy()

        # Type of concept instance
        self.category = category

        # Set up the concept instance class
        if self.category is not Concept.ABSTRACT:
            self._instance_class = Instance

            if self.category is Concept.STATIC:
                self._instance = self._instance_class(self.name, properties=self.properties)

    def __str__(self): return self.name
    def __repr__(self): return "<Concept: {}>".format(self.name)

    def __hash__(self):
        if not self.__dict__: return 0
        return hash(self.name)

    @property
    def parents(self):
        return self._parents
    @parents.setter
    def parents(self, conceptSet: FamilyConceptSet):
        if isinstance(conceptSet, FamilyConceptSet) and conceptSet.isAncestors():
            self._parents = conceptSet
            conceptSet._owner = self
        else:
            raise ConsistencyError("Incorrect definition of {}'s parent set. Passed {}".format(self, conceptSet))

    @property
    def children(self):
        return self._children
    @children.setter
    def children(self, conceptSet: FamilyConceptSet):
        if isinstance(conceptSet, FamilyConceptSet) and not conceptSet.isAncestors():
            self._children = conceptSet
            conceptSet._owner = self
        else:
            raise ConsistencyError("Incorrect definition of {}'s children set. Passed {}".format(self, conceptSet))


    @property
    def category(self): return self._category
    @category.setter
    def category(self, category: str):
        if   category == self.ABSTRACT: self._category = self.ABSTRACT
        elif category == self.STATIC: self._category = self.STATIC
        elif category == self.DYNAMIC: self._category = self.DYNAMIC
        else: raise ValueError("Invalid category '{}' provided to concept {} definition".format(category, self.name))

    def ancestors(self):
        """ Return a collection of concepts, all of the concepts that can be linked via the parent
        link. All the ancestor concepts are returned.

        Returns:
            ancestors ({Concept}) - The collection
        """

        ancestors = self.parents.copy()  # Add the parents of this concept as the initial set

        for parent in self.parents:  # Recursively collect the parents of the collected concepts
            if isinstance(parent, str):
                ancestors.add(parent)
            else:
                ancestors = ancestors.union(parent.ancestors())

        return ancestors

    def descendants(self):
        """ Return a collection of child concepts linked to the current concept

        Returns:
            descendants ({Concept}) - The collection of descendant concepts
        """

        decendants = self.children.copy()

        for child in self.children:
            if isinstance(child, str):
                decendants.add(child)
            else:
                decendants = decendants.union(child.descendants())

        return decendants

    def setInstanceClass(self, instance_class: Instance) -> None:
        """ Overload the default ConceptInstance with another that extends ConceptInstance such that
        when new instances of this class are generated they shall be instances of the new class. In
        the event that the concept is static, the concept instance is replaced.

        Params:
            instance_class (ConceptInstance): The class object

        Raises:
            TypeError: In the event that the instance_class is does not extend ConceptInstance
        """

        if not issubclass(instance_class, Instance):
            raise TypeError("Class passed to concept '{}' as new instance".format(self) +
                            " class does not extend Instance and is type {}".format(type(instance_class)))

        self._instance_class = instance_class

        if self.category is Concept.STATIC:
            self._instance = self._instance_class(self, properties=self.properties)

    def instance(self, instance_name: str = None, properties: dict = None) -> Instance:
        """ Generate an instance of this concept and return it. In the event that the concept is
        static, this function acts as a singleton and returns the single instance of this concept

        Params:
            instance_name (str): (dynamic only) An unique identifier for the instance - defaults to
                UUID in the event that it is not provided and needed
            properties (dict): (dynamic only) A collection of properties for this instance, overloads concept properties

        Raises:
            TypeError: In the event that the concept is abstract - no instance can be created
        """

        if self.category is Concept.ABSTRACT:
            raise TypeError("Concept {} is abstract - No instances can be generated for this concept")

        if self.category is Concept.STATIC:
            if instance_name is not None:
                log.warning("{} concept is static yet instance called for with an identifier".format(self.name))
            return self._instance

        if instance_name is None: instance_name = str(uuid.uuid4())
        props = self.properties.copy() if properties is None else properties

        return self._instance_class(self.name, instance_name, props)  # Generate a new instance of this class

    def clone(self):
        """ Return an new partial concept with identical information but invalid concept connections

        Returns:
            Clone (Concept) - A new partial concept
        """
        clone = Concept(
            self.name,
            {p.name for p in self.parents},
            {c.name for c in self.children},
            self.alias,
            self.properties,
            self.category
            )

        return clone

    def minimise(self) -> dict:
        """ Return only the information the concept represents

        Returns:
            dict - The minimised version of the concept, encapsulates all the information
        """

        concept = {"name": self.name}
        if self.parents: concept["parents"] = sorted([parent if isinstance(parent, str) else parent.name
            for parent in self.parents])
        if self.properties: concept["properties"] = self.properties
        if self.alias: concept["alias"] = sorted(list(self.alias))
        if self.category is not Concept.DYNAMIC: concept["category"] = self.category

        return concept

    @classmethod
    def expandConceptSet(cls, collection, descending: bool = True):
        """ Expand a collection of concepts to include all descendants when applicable

        Params:
            collection (set): The initial set of concepts, that are to be expanded

        Returns:
            set: A superset of the collection, includes children
        """

        expansion = set()

        for concept in collection:
            expansion.add(concept)
            if isinstance(concept, cls):
                group = concept.descendants() if descending else concept.ancestors()
                for con in group:
                    if isinstance(con, str) or con.category is not Concept.ABSTRACT:
                        expansion.add(con)

        log.debug("expanded set {} into {}".format([str(x) for x in collection], [str(x) for x in expansion]))
        return expansion

    @classmethod
    def minimiseConceptSet(cls, collection, ascending: bool = True):
        """ Minimise a collection according to possible concepts within another.

        Params:
            collection (set): The collection that is being minimised

        Returns:
            set: Minimised set
        """
        collection = set(collection)
        minimised = set()

        for con in collection:
            if isinstance(con, cls):
                group = con.ancestors() if ascending else con.descendants()
                if group.intersection(collection): continue

            minimised.add(con)

        log.debug("minimised set {} from {}".format([str(x) for x in minimised], [str(x) for x in collection]))
        return minimised