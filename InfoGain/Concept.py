class Concept:

    def __init__(self, name: str, permeable = False ):
        self.name = name
        self.permeable = permeable
        self.parents = set()
        self.children = set()

    def __str__(self):
        return ">" + self.name + "<"

    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def isParentOf(self, concept) -> bool:
        return concept in self.children

    def isAncestorOf(self, concept) -> bool:
        return concept in set([child for child in self.descendants()]) 

    def isChildOf(self, concept) -> bool:
        return concept in self.parents

    def isDecendantOf(self, concept) -> bool:
        return concept in set([parent for parent in self.ancestors()])

    def addParent(self, parent):
        """ Record the added parent concept, raise issue with overwritting """
        if parent in self.parents:
            raise ValueError( "Attempted overwritting of parent: " + parent.name )
        self.parents.add(parent)

    def removeParent(self, parent) -> None:
        self.parents.remove(parent)

    def addChild(self, child):
        """ Record the added child concept, raise issue with overwritting """
        if child in self.children:
            raise ValueError( "Attempted overwritting of child: " + child.name )
        self.children.add(child)

    def removeChild(self, child) -> None:
        self.children.remove(child)

    def ancestors(self):
        """ Return a collection of parent concepts """

        ancestors = self.parents.copy()

        for parent in self.parents:
            ancestors = ancestors.union(parent.ancestors())

        return ancestors

    def descendants(self):
        """ Return a collection of parent concepts """

        decendants = self.children.copy()

        for child in self.children:
            decendants = decendants.union(child.descendants())

        return decendants

    def isCircular(self, ancestors = [], decendants = [] ):
        """ Raises a value error if the concept is linked in a circular fashion with
        other concepts.

        Params:
            ancestors : A list of concept names that are children of the current concept.
            decendants: A list of concept names that are parents of the current concept.
        """

        for concept in ancestors:
            if concept in self.parents.keys():
                raise ValueError( "Circular expression found." )

        for concept in decendants:
            if concept in self.children.keys():
                raise ValueError( "Circular expression found." )

        for p in self.parents.values():
            p.isCircular( ancestors = ancestors + [self.name] )

        for c in self.children.values():
            c.isCircular( decendants = decendants + [self.name] )