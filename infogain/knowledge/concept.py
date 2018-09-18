import logging
log = logging.getLogger(__name__)

class Concept:
    """ A concept represents a "thing", an idea, an object, a place, anything.

    Args:
        name (str): The name/representation for the concept
        parents (set): A set of concepts/strings that represent parent concepts
        children (set): A set of concepts/strings that represent child concepts
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
        json: dict = {}):

        self.name = name

        if json:
            self.alias = set(json.get("alias", alias))
            self.properties = json.get("properties", {})
            self.category = json.get("category", category)

            self.parents = set(json.get("parents", parents))
            self.children = set(json.get("children", children))
        
        else:
            self.alias = set(alias)
            self.properties = properties.copy()
            self.category = category

            self.parents = parents.copy()
            self.children = children.copy()

        [Concept.fuse(self, par) for par in self.parents if not isinstance(par, str)]
        [Concept.fuse(self, child) for child in self.children if not isinstance(child, str)]

    def __str__(self): return self.name

    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if not self.__dict__: return 0
        return hash(self.name)

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

    @staticmethod
    def fuse(concept_one, concept_two):
        """ Ensure that the provided concepts point to one another in the correct manner """

        if concept_one in concept_two.parents or concept_two in concept_one.children:

            concept_one.children = {concept_two}.union(concept_one.children)
            concept_two.parents = {concept_one}.union(concept_two.parents)

        if concept_one in concept_two.children or concept_two in concept_one.parents:

            concept_one.parents = {concept_two}.union(concept_one.parents)
            concept_two.children = {concept_one}.union(concept_two.children)

class Instance(Concept):
    """ A geniune instance of a concept existing in the knowledge. An instance is of a particular concept. """
    
    def __init__(self, name: str, parent: Concept, properties={}):
        self.name = name
        self.parent = parent

        # Combine the provided properties of the instance with the concept properties if applicable
        self.properties = {**parent.properties, **properties} if isinstance(parent, Concept) else properties