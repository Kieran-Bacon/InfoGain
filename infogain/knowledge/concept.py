import uuid
import weakref
import collections

from ..information import Vertex
from .instance import Instance
from ..exceptions import ConsistencyError

import logging
log = logging.getLogger(__name__)

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
        aliases: set = set(),
        properties: dict = {},
        category: str = "dynamic"
        ):

        self.name = name
        self.category = category

        # Set up concept container objects to manage various interactions of the concept
        # Container of relationships this concept is a member of - weak to remove relations if ever they are deleted
        self._relationMembership = weakref.WeakSet()  # Hold relations this concept is a member of
        self._parents = FamilyConceptSet(weakref.ref(self), ancestors=True)  # Hold references to parent concepts
        self._children = FamilyConceptSet(weakref.ref(self), ancestors=False)  # Hold references to child concepts
        self._aliases = ConceptAliases(weakref.ref(self))  # Hold the various ways concepts might be referenced
        self._properties = ConceptProperties(weakref.ref(self))  # Hold property information on a concept

        # Add container information
        for con in parents: self.parents.add(con)
        for con in children: self.children.add(con)
        for alias in aliases: self.aliases.add(alias)
        self.properties.update(properties)

        # Set up the concept instance class
        if self.category is not Concept.ABSTRACT:
            self._instance_class = Instance

            if self.category is Concept.STATIC:
                self._instance = self._instance_class(self.name, properties=self.properties)

    def __str__(self): return self.name
    def __repr__(self): return "<Concept: {}>".format(self.name)
    def __hash__(self): return hash(self.name)

    @property
    def parents(self):
        return self._parents
    @parents.setter
    def parents(self, conceptSet: collections.abc.MutableSet):

        if any(not isinstance(concept, Concept) for concept in conceptSet):
            raise ValueError("You cannot provide a non Concept as a parent of concept {}".format(self))

        conceptSet = set(conceptSet)

        toAdd = conceptSet.difference(self._parents)
        toRemove = self._parents.difference(conceptSet)

        for rConcept in toRemove:
            self._parents.remove(rConcept)

        for aConcept in toAdd:
            self._parents.add(aConcept)

    @property
    def children(self):
        return self._children
    @children.setter
    def children(self, conceptSet: collections.abc.MutableSet):

        if any(not isinstance(concept, Concept) for concept in conceptSet):
            raise ValueError("You cannot provide a non Concept as a child of concept {}".format(self))

        conceptSet = set(conceptSet)

        toAdd = conceptSet.difference(self._children)
        toRemove = self._children.difference(conceptSet)

        for rConcept in toRemove:
            self._children.remove(rConcept)

        for aConcept in toAdd:
            self._children.add(aConcept)

    @property
    def category(self): return self._category
    @category.setter
    def category(self, category: str):
        if   category == self.ABSTRACT: self._category = self.ABSTRACT
        elif category == self.STATIC: self._category = self.STATIC
        elif category == self.DYNAMIC: self._category = self.DYNAMIC
        else: raise ValueError("Invalid category '{}' provided to concept {} definition".format(category, self.name))

    @property
    def aliases(self): return self._aliases

    @property
    def properties(self): return self._properties

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
        if self.category is Concept.ABSTRACT:
            raise ConsistencyError("An abstract concept cannot have an instance, nor a instance class set")

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
            self.aliases,
            self.properties,
            self.category
            )

        return clone

class ConceptSet(collections.abc.MutableSet):
    """ The Concept set is a container for concepts that provides additional support for many of the operations that
    require concepts. The ConceptSet intends to keep track of partial concepts that have been used as placeholders and
    allow for easy updates to those concepts. Furthermore it helps expand and minimise a set of concepts via their
    family hierarchy

    Params:
        iterable {Concept}: An initial iterable of the concept objects
    """

    def __init__(self, iterable: {Concept} = set()):
        self._elements = set()
        self._partial = set()

        # Add the items into the ConceptSet
        for con in iterable: self.add(con)

    def __bool__(self): return bool(self._elements)
    def __iter__(self): return iter(self._elements)
    def __contains__(self, concept: Concept): return concept in self._elements
    def __len__(self): return len(self._elements)
    def __repr__(self): return "<ConceptSet{}>".format(self._elements)

    def add(self, concept: Concept):
        """ Add a concept (or partial concept) into the concept set.

        Params:
            concept (Concept): the concept to be added
        """
        if isinstance(concept, str):
            if concept in self._elements: return  # Cannot add a partial if its already in elements
            self._partial.add(concept)  # Record that this added concept is only partial
        elif concept in self._partial:
            # This is a non partial element to replace the current partial element
            self._elements.remove(concept)  # Remove the partial element
            self._partial.remove(concept)  # Remove the partial tag

        # Add the element into the set
        self._elements.add(concept)

    def discard(self, concept: Concept) -> None:
        """ Remove a concept from the ConceptSet

        Params:
            concept (Concept): The concept to be removed
        """

        isDiscarded = False


        if concept in self._elements:
            self._elements.remove(concept)
            isDiscarded = True
        if concept in self._partial:
            self._partial.remove(concept)
            isDiscarded = True

        return isDiscarded

    # def remove(self, concept: Concept) -> None:
    #     """ Remove a concept from the ConceptSet

    #     Params:
    #         concept (Concept): The concept to be removed

    #     Raises:
    #         KeyError: In the event that the concept is not present within the ConceptSet
    #     """
    #     self._elements.remove(concept)
    #     if concept in self._partial: self._partial.remove(concept)

    def expand(self, descending: bool = True) -> None:
        """ Expand a collection of concepts to include either their descendants or their ancestors when applicable

        Params:
            descending (bool): Dictate the direction of expansion
        """
        for concept in self._elements.copy():
            if isinstance(concept, Concept):
                group = concept.descendants() if descending else concept.ancestors()
                for con in group:
                    self.add(con)

    def expanded(self, descending: bool = True) -> None:
        """ Return a new ConceptSet that shall be a superset of this set, and contain the descendants / ancestors of
        each member concept

        Params:
            descending (bool): Indicate whether the new set should be expanded to include the descendants or ancestors
        """
        copy = self.copy()
        copy.expand(descending)
        return copy

    def minimise(self, ascending: bool = True) -> None:
        """ Reduce this set to contain either the most generic concepts (higher) or the most specific (bottom) level
        concepts of the member concepts by navigating the concept's family structure.

        Params:
            collection (set): The collection that is being minimised
        """
        minimised = set()

        for con in self._elements:
            if isinstance(con, Concept):
                group = con.ancestors() if ascending else con.descendants()
                if group.intersection(self): continue

            minimised.add(con)

        self._elements = minimised
        self._partial = self._partial.intersection(self._elements)  # Reduce the partial set

    def minimised(self, ascending: bool = True) -> None:
        """ Return a Subset of this ConceptSet that contains either the highest/lowest level concepts

        Params:
            ascending (bool): An indicator that determines in which direction the reduction occurs
        """
        copy = self.copy()
        copy.minimise(ascending)
        return copy

    def toStringSet(self) -> {str}:
        """ Generate a conventional set of concept names (str) from this concept set and return

        Returns:
            {str}: A set of concept names which are strings
        """
        return {c if isinstance(c, str) else c.name for c in self}

    def union(self, other: set) -> set:
        """ Return a set that is the unification of the this set and the other set. This method shall prefer Concrete
        concepts.

        Params:
            other (ConceptSet): The set for this set to union with

        Returns:
            ConceptSet: The concept set that contains all concepts in both this set and the other set
        """
        return ConceptSet([e for e in self._elements] + [e for e in other])

    def intersection(self, other: set) -> set:
        """ Find the concepts that appear in both this ConceptSet and the other ConceptSet, choosing the concrete
        concepts as preference

        Params:
            other (ConceptSet): The other set to intersect with

        Returns:
            ConceptSet: The set of concepts found in both this set and the other set
        """
        group = ConceptSet()

        # Add all elements intersected elements into the new set
        for c in self:
            if c in other:
                group.add(c)

        # Add the same intersected elements - to resolve any partial links
        for c in other:
            if c in self:
                group.add(c)

        return group

    def difference(self, other: set) -> set:
        """ Return a ConceptSet of the concepts from this set, that do not appear in the other set

        Params:
            other (ConceptSet): The set to query for membership, to not be found in

        Returns:
            ConceptSet: A set of all concepts from this set, that do not appear in the other set
        """
        return ConceptSet((e for e in self._elements if e not in other))

    def copy(self):
        """ Shallow copy this set """
        return ConceptSet(self._elements)

    def partials(self) -> {str}:
        """ Provide a set of the partial concepts within the set

        Returns:
            {str}: A set of concept names yet to be linked correctly
        """
        return self._partial.copy()

class FamilyConceptSet(ConceptSet):
    """ A set to hold information of a family hierarchy. Concepts held in this set are the parents or children of the
    concept that holds this set. The set is responsible for making consisten this relationship with the concepts in this
    set.

    Params:
        owner (Concept): The concept that owns this Family Concept, the concept this instance is working for
        ancestors (bool): Indicates whether this set holds the the parents or children for the owner
    """

    def __init__(self, owner: weakref.ProxyType, ancestors: bool = True):

        self._owner = owner
        self._elements = set()
        self._partial = set()
        self._ancestors = ancestors

    def __repr__(self): return "<FamilyConceptSet{}>".format(self._elements if self._elements else r"{}")

    def add(self, concept: Concept) -> None:
        """ Add a concept into this set. If the concept is partial, store its information such that it can be replaced
        at a later date. If this is the parent set, pull down relations that have been set up on the concepts within.
        Automatically link this relation with the added concept if they haven't already been linked with this concept.

        Params:
            concept (Concept): The concept to be added into the set
        """

        #TODO: Need to work out how to ensure that we can't add the same concept over and over again

        # There are two types of input - Concept and string
        # We want to add a full concept in the event that it doesn't exist or that the one that does exist is partial
        # We want to add the string in the event that it doesn't exist

        # empty, add concept
        # empty add string
        # concept, add concept - ignore
        # concept, add string - ignore
        # string, add concept
        # string, add string - ignore

        # Add the element into the set via ConceptSet method
        super().add(concept)
        if not isinstance(concept, Concept): return  # Do not attempt to connect family with partial concept

        owner = self._owner()  # Get the true concept object

        # Identify corresponding family concept set from new concept + pull down relations where applicable
        if self._ancestors:
            # This set holds the ancestors of its owner

            # Pull down aliases
            for alias in concept.aliases:
                owner.aliases._addInherited(alias)

            # Pull down properties
            for key, value in concept.properties.items():
                owner.properties._setInherited(key, value)

            # Pull down relations from the new parent concept
            for relation in concept._relationMembership:
                owner._relationMembership.add(relation)
                relation.subscribe(owner)

            otherSet = concept.children

        else:
            # This set holds the descendants of the owner
            otherSet = concept.parents

        # Check whether the owning concept is correctly linked with the new concept from their perspective
        if not otherSet._linked(owner):
            otherSet.add(owner)

    def _linked(self, concept: Concept):
        """ Determine whether this concept is correctly linked inside this concept set. Linked if the concept is within
        the set and isn't partial.

        Params:
            concept (Concept): The concept that is being checked if correctly a member
        """
        return concept not in self._partial and concept in self._elements

    def discard(self, concept: Concept) -> bool:

        isRemoved = super().discard(concept)

        if isRemoved and isinstance(concept, Concept):
            # The concept was present

            #TODO need to ensure that the concepts are delinked, the inherited aliases, properties are removed - tested
            raise NotImplementedError()

class ConceptAliases(collections.abc.MutableSet):

    def __init__(self, owner: weakref.ProxyType):
        self._owner = owner
        self._elements = set()
        self._inheritedCounter = collections.defaultdict(int)

    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements)
    def __contains__(self, name: str): return name in self._elements

    def add(self, name: str):
        if not isinstance(name, str):
            raise TypeError("Invalid type of alias given - aliases must be str not {}".format(type(name)))

        if name in self._elements: return

        self._elements.add(name)
        for child in filter(lambda x: isinstance(x, Concept), self._owner().descendants()):
            child.aliases._addInherited(name)

    def _addInherited(self, name: str):
        self._elements.add(name)
        self._inheritedCounter[name] += 1

    def discard(self, name: str):

        if (
            not isinstance(name, str) or
            name not in self._elements or
            (name in self._inheritedCounter and self._inheritedCounter[name])
        ):
            # Invalid item passed to discard to be removed
            return False

        if name not in self._elements or self._inheritedCounter[name]:
            # The name doesn't exist or the name is inherited from another
            return False

        self._elements.remove(name)

        for child in filter(lambda x: isinstance(x, Concept), self._owner().descendants()):
            child.aliases._discardInherited(name)

        return True

    def _discardInherited(self, name: str):

        if name not in self._inheritedCounter or not self._inheritedCounter[name]: return False

        self._inheritedCounter[name] -= 1

        # If the counter had dropped to zero - remove the name from the alias pool
        if not self._inheritedCounter[name]:
            del self._inheritedCounter[name]
            self._elements.remove(name)

    def inherited(self):
        return set(self._inheritedCounter.keys())

    def specific(self):
        return self._elements.difference(self.inherited())

class MultiplePartProperty(collections.abc.MutableSet):

    def __init__(self, iterable = None):
        self._elements = collections.Counter(iterable)

    def __repr__(self): return "<MultiPartProperty {}>".format(set(self._elements.keys()))
    def __len__(self): return len(self._elements)
    def __iter__(self): return iter(self._elements.keys())
    def __contains__(self, item: object): return item in self._elements
    def add(self, item: object, count = 1): self._elements[item] += max(1, count)

    def discard(self, item: object):

        if item not in self._elements: return False

        self._elements[item] -= 1

        if not self._elements[item]:
            del self._elements[item]

        return True

class ConceptProperties(collections.abc.MutableMapping):

    def __init__(self, owner: weakref.ProxyType):
        self._owner = owner
        self._elements = {}
        self._inheritedElements = {}
        self._inheritedCounter = collections.defaultdict(int)

    def __len__(self): return len(set(self._elements.keys()).union(set(self._inheritedElements.keys())))
    def __iter__(self): return iter({**self._inheritedElements, **self._elements})

    def __setitem__(self, key: str, value: object):
        """ Set the value for a property value on the concept. There are three states a property can have: It can not be
        set which results in a new property being added; It can be set and the new value is the same as the old, nothing
        happens; propery was set and has now changed.

        Set the correct value and desceminate if the value is new or changed

        """

        if not isinstance(key, str): raise ValueError("Property name must be a `str` not `{}`".format(type(key)))
        if value is None: raise ValueError("Cannot set concept property as None")

        # Collect the owning concept
        owner = self._owner()

        # Check to see if the value had already been set beforehand
        if key in self._elements:
            # The value has been set before
            if value == self._elements[key]: return  # Nothing to do


            old_value, self._elements[key] = self._elements[key], value

            for child in filter(lambda x: isinstance(x, Concept), owner.children):
                child.properties._updateInherited(key, old_value, value)

        else:
            # The item is entirely new
            self._elements[key] = value

            if key in self._inheritedElements:
                # The key was inherited before and therefore children already have an inherited property with this
                # key. Update their key value to show this new one
               for child in filter(lambda x: isinstance(x, Concept), owner.children):
                    child.properties._updateInherited(key, self._inheritedElements[key], value)

            else:
                # New for children too, set inherited value
                for child in filter(lambda x: isinstance(x, Concept), owner.children):
                    child.properties._setInherited(key, value)

    def __getitem__(self, key: str):
        if key in self._elements: return self._elements[key]
        elif key in self._inheritedElements: return self._inheritedElements[key]
        else: raise KeyError("{} doesn't have a property by that name {}".format(self._owner(), key))

    def __delitem__(self, key: str):

        # Deleting an property when there is another with the same key in your inherited, it must then be cascaded
        # in the event that its value is not the same as the one you've just removed.

        # Removing an item should trigger the children of this concept to remove this as an inherited item

        # Remove the stored value from the elements
        value = self._elements.pop(key)

        owner = self._owner()

        # If there was an inherited value with the same value, and the value is not the same as specific value, cascade
        if key in self._inheritedElements:
            if self._inheritedElements[key] != value:  # If the value is the same, no need to do anything
                for child in owner.children:
                    child.attr._updateInherited(key, self._inheritedElements[key])

        else:
            # The value has been completely removed - remove this property from children where it may have cascaded
            for child in filter(lambda x: isinstance(x, Concept), owner.children):
                child.attr._removeInherited(key, value)

    def _setInherited(self, key: str, value: object):
        """ This is a key value that is being passed down by an unknown parent concept - the assumption is that the
        parent concept that gives this attribute shall never give it twice, and shall call update if it would like to
        change its value. Given this, a count is used to record the number of parents that provide the said property.

        If conflicting values for keys are givening by inheriting a value, both shall be recorded against the key. It
        will be up to the user to either select them at random or overload the inherited value with a specifc value for
        the concept.

        Params:
            key (str): The string name of the property
            value (object): What ever would like to be recorded against the key
        """
        if value is None: raise ValueError("Cannot set concept property as None")

        if key in self._inheritedElements:
            # Previously inherited something with that key

            storedVal = self._inheritedElements[key]

            if isinstance(storedVal, MultiplePartProperty):
                # There have been multiple inherited conflicts, ading to the MultiPartProperty this addition
                storedVal.add(value)

            elif value != storedVal:
                # There was an initial value that had no conflict - create multi prop and add original count times
                mprop = MultiplePartProperty()
                mprop.add(storedVal, count=self._inheritedCounter[key])
                mprop.add(value)

                self._inheritedElements[key] = mprop

        else:
            # New inherited item
            self._inheritedElements[key] = value

        # Update counter for a key
        self._inheritedCounter[key] += 1

        if key not in self._elements:
            # The inherited key wasn't overloaded by the concept so it needs to propagate
            for child in self._owner().children:
                child.properties._setInherited(key, value)

    def _updateInherited(self, key: str, oldValue: object, value: object):
        """ For the given inherited value key that this container shall already have, change the value if possible to
        the newly provided value

        Params:
            key (str): the name of the property
            value (object): the value of the property to replace to old one
        """

        if key not in self._inheritedElements:
            raise ValueError("Properties don't have inherited property with given key {}".format(key))

        inheritedProp = self._inheritedElements[key]

        if isinstance(inheritedProp, MultiplePartProperty):
            inheritedProp.remove(oldValue)
            inheritedProp.add(value)

            if len(inheritedProp) == 1:
                # All the properties now agree with each other, no conflict
                self._inheritedElements[key] = inheritedProp.pop()

        elif inheritedProp == oldValue:
            if self._inheritedCounter[key] == 1:
                # The value being updated was the only value inherited, just switch it and end
                self._inheritedElements[key] = value

            else:
                # Multiple parts provided the old value - now switching between properties so a multipart needed
                multiprop = MultiplePartProperty()
                multiprop.add(inheritedProp, count=self._inheritedCounter[key] - 1)
                multiprop.add(value)

        else:
            raise ValueError("Original property value to be updated didn't match stored value - found {} not {}".format(
                inheritedProp, oldValue
            ))

        if key not in self._elements and inheritedProp != value:
            # The update needs to cascade down into the child concepts
            for child in self._owner().children:
                child.properties._updateInherited(key, oldValue, value)

    def _removeInherited(self, key: str, value: object):
        """ Remove an inherited key, value """

        if key not in self._inheritedElements:
            raise ValueError("Cannot remove inherited property not inherited - {}".format(key))

        inheritedProp = self._inheritedElements[key]

        if isinstance(inheritedProp, MultiplePartProperty):
            inheritedProp.remove(value)

            if len(inheritedProp) == 1:
                self._inheritedElements[key] = inheritedProp.pop()

        elif inheritedProp == value:

            self._inheritedCounter[key] -= 1

            if not self._inheritedCounter[key]:
                del self._inheritedElements[key]
                del self._inheritedCounter[key]

        else:
            raise ValueError(
                "Cannot remove property when uncertainty about property value"
                " - found {} when expected {}".format(inheritedProp, value)
            )

        self._inheritedCounter[key] -= 1

        if key not in self._elements:
            # The value had cascaded, need to remove from children

            for child in self._owner().children:
                child.properties._removeInherited(key, value)

    def copy(self):
        return dict(self.items())