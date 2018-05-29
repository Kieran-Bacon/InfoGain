class Concept:

    def __init__(self, name: str, content = {}):
        self.name = name
        self._state = "valid"

        self.parents = set()
        self.children = set()
        self.text = set(content.get("textRepr", []))

        self.permeable = content.get("permeable", False)
        self._properties = content.get("properties",{})

    def __str__(self):
        return "<c 'state'='" + self._state + "'>" + self.name + "</c>"

    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def clone(self):
        """ Return an new partial concept with identical information but invalid concept connections
        """

        clone = Concept(self.name, {"permeable": self.permeable, "properties": self._properties.copy()})

        clone._state = "clone"
        clone.parents = {p.name for p in self.parents}
        clone.children = {c.name for c in self.children}

        return clone

    def addRepr(self, text: str):
        """ Add the representation into the set """
        self.text.add(text)

    def textRepr(self):
        """ Return the representations of the concept """
        return self.text

    def addProperty(self, name: str, value) -> None:
        self._properties[name] = value
        return

    def removeProperty(self, name: str) -> None:
        if name in self._properties:
            del self._properties[name]
        return

    def property(self, prop: str):
        return self._properties["prop"]

    def properties(self):
        return self._properties.keys()

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

    def minimise(self) -> dict:
        """ Return only the information the concept represents """
        concept = {
            "name": self.name,
            "parents" : [parent.name for parent in self.parents],
        }

        if len(self.text): concept["textRepr"] = list(self.text)
        if len(self._properties): concept["properties"] = self._properties
        if self.permeable: concept["permeable"] = True

        return concept

    def isCircular(self, ancestors = [], decendants = [] ):
        """ Raises a value error if the concept is linked in a circular fashion with
        other concepts.

        Params:
            ancestors : A list of concept names that are children of the current concept.
            decendants: A list of concept names that are parents of the current concept.
        """

        for concept in ancestors:
            if concept in self.parents:
                raise ValueError( "Circular expression found." )

        for concept in decendants:
            if concept in self.children:
                raise ValueError( "Circular expression found." )

        for p in self.parents:
            p.isCircular( ancestors = ancestors + [self.name] )

        for c in self.children:
            c.isCircular( decendants = decendants + [self.name] )