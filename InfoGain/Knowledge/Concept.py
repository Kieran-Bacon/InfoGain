class Concept:
    """ A concept represents a "thing", an idea, an object, a place, anything.

    Args:
        name (str): The name/representation for the concept
        parents (set): A set of concepts/strings that represent parent concepts
        children (set): A set of concepts/strings that represent child concepts
        json (dict): The concept information in the form of a diction, expected from json
    """

    def __init__(self, name: str, parents: set = set(), children: set = set(), json: dict = {}):
        self.name = name
        self.alias = set()
        self.properties = {}
        self.permeable = False

        self.parents = parents.copy()
        self.children = children.copy()

        if json:
            self.alias = set(json.get("alias", []))
            self.properties = json.get("properties", {})
            self.permeable = json.get("permeable", False)

            self.parents = set(json.get("parents", []))
            self.children = set(json.get("children", []))

    def __str__(self): return self.name

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
        clone.alias = self.alias.copy()
        clone.properties = self.properties.copy()
        clone.permeable = self.permeable

        return clone

    def ancestors(self):
        """ Return a collection of parent concepts """

        ancestors = self.parents.copy()

        for parent in self.parents:
            if isinstance(parent, str):
                ancestors.add(parent)
            else:
                ancestors = ancestors.union(parent.ancestors())

        return ancestors

    def descendants(self):
        """ Return a collection of parent concepts """

        decendants = self.children.copy()

        for child in self.children:
            if isinstance(child, str):
                decendants.add(child)
            else:
                decendants = decendants.union(child.descendants())

        return decendants

    def minimise(self) -> dict:
        """ Return only the information the concept represents """
        concept = {
            "name": self.name,
            "parents" : [parent if isinstance(parent, str) else parent.name for parent in self.parents],
            "children": [child if isinstance(child, str) else child.name for child in self.children],
            "properties": self.properties,
            "alias": list(self.alias),
            "permeable": self.permeable
        }

        return concept