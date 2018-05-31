class Concept:

    def __init__(self, name: str, parents: set = None, children: set = None, json: dict = {}):
        self.name = name
        self.representations = set()
        self.properties = {}
        self.permeable = False

        self.parents = parents.copy() if parents else set()
        self.children = children.copy() if children else set()

        if json:

    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def clone(self):
        """ Return an new partial concept with identical information but invalid concept connections """
        clone = Concept(self.name,
            {p.name for p in self.parents},
            {c.name for c in self.children})
        clone.representations = self.representations
        clone.properties = self.properties
        clone.permeable = self.permeable

        return clone

    def isParentOf(self, concept) -> bool:
        return concept in self.children

    def isAncestorOf(self, concept) -> bool:
        return concept in set([child for child in self.descendants()]) 

    def isChildOf(self, concept) -> bool:
        return concept in self.parents

    def isDecendantOf(self, concept) -> bool:
        return concept in set([parent for parent in self.ancestors()])

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
            "properties": self.properties,
            "representations": list(self.representations),
            "permeable": self.permeable
        }

        return concept
