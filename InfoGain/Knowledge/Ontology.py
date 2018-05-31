import json

from . import MissingConcept
from .Concept import Concept
from .Relation import Relation

class Ontology:
    """ An ontology is a collection of knowledge, it contains a collection of concepts
    and the relationships between them.

    Args:
        name (str): The name given to the ontology
        filepath (str): The location of a saved ontology to expand
    """

    def __init__(self, name: str = None, filepath: str = None):

        # Simply idenfitication of the ontology, no functional use
        self.name = name
        self._concepts = {}                     # Unique concept store
        self._relations = {}                    # Unique relation store

        if filepath:

            # Extract the information from the input ontology file
            with open(filepath) as ontologyFile:
                data = json.load(ontologyFile)

            # Define the name
            if "name" in data: self.name = data["name"]

            # Create the concepts and add them to the ontology store without warnings
            for name, rawConcept in data.get("Concepts", {}).items():
                concept = Concept(name, json=rawConcept)
                self.addConcept(concept)

            # Create the relations within the system
            for name, rawRelation in data.get("Relations", {}).items():

                # For each set of relations found in the system
                for conceptSet in rawRelation["concepts"]:
                    domains = {self.concept(con) for con in conceptSet["domains"]}
                    targets = {self.concept(con) for con in conceptSet["targets"]}

                    if None in domains.union(targets): raise MissingConcept("Relation '"+name+"' references unknown concept.")

                    self.addRelation(Relation(domains, name, targets))

    def addConcept(self, concept: Concept) -> None:
        """ Add concept object to ontology, overwrite previous concept if present.
        Identifies the relation ships concepts parent objects are and becomes members to those
        relations if applicable. """

        for con in concept.parents:
            name = con if isinstance(con, str) else con.name
            parent = self.concept(name)

            if parent:
                # Align parent to child
                parent.children.discard(concept)
                parent.children.add(concept)

                # Ensure concept ontology alignment
                concept.parents.remove(con)
                concept.parents.add(parent)

        for con in concept.children:
            name = con if isinstance(con, str) else con.name
            child = self.concept(name)

            if child:
                # Align child concept
                child.parents.discard(concept)
                child.parents.add(concept)

                # Ensure concept ontology aligment
                concept.children.remove(con)
                concept.children.add(child)
                
        # Save concept
        self._concepts[concept.name] = concept
        [instance.subscribe(concept) for relation in self._relations.values() for instance in relation]

    def addRelation(self, relation: Relation) -> None:
        """ Add a relation to the ontology store, ensuring to create a new slot if not previously seen """

        for con in relation.domains:
            if isinstance(con, str):
                con = self.concept(con)
                if con is None:
                    raise MissingConcept("Newly added relation '"+relation.name+"' references concepts not in ontology")
                else:
                    relation.domains.remove(con)
                    relation.domains.add(con)

        for con in relation.targets:
            if isinstance(con, str):
                con = self.concept(con)
                if con is None:
                    raise MissingConcept("Newly added relation '"+relation.name+"' references concepts not in ontology")
                else:
                    relation.targets.remove(con)
                    relation.targets.add(con)

        pairing = self._relations.get(relation.name, set())
        pairing.add(relation)
        self._relations[relation.name] = pairing

    def concept(self, conceptName: str) -> Concept:
        return self._concepts.get(conceptName, None)

    def concepts(self) -> [Concept]:
        """ Return a list of concepts found within the ontology, order is non deterministic """
        return list(self._concepts.values())

    def relation(self, relationName: str) -> Relation:

        collection = self._relations.get(relationName, None)
        if collection and len(collection) == 1: collection = list(collection)[0]
        return collection

    def relations(self) -> [str]:
        return list(self._relations.values())

    def findRelations(self, domain: str, target: str):
        """ Return a list of relations that could be formed between the domain and the target """
        dom, tar = self.concept(domain), self.concept(target)
        if None in (dom, tar):
            raise Exception("Invalid concepts provided when looking for relations")

        for relation in self.relations():
            if relation.hasDomainTargetPair(dom, tar):
                yield relation

    def clone(self):
        """ Create a new ontology object that is a deep copy of this ontology instance """

        ontologyClone = Ontology(self.name)

        # Clone concepts
        [ontologyClone.addConcept(con.clone()) for con in self.concepts()]

        # Clone relationships
        for group in self._relations.values():
            for relation in group:
                domains = {ontologyClone.concept(dom.name) for dom in relation.domains}
                targets = {ontologyClone.concept(tar.name) for tar in relation.targets}
                ontologyClone.addRelation(Relation(domains, relation.name, targets))

        return ontologyClone

    def save(self, folder: str = "./", filename: str = None) -> None:
        """ Save the file to the current working directory or the filename provided """

        import os, uuid

        if filename is None and self.name is None: filename = uuid.uuid4().hex
            
        ontology = {
            "name": self.name if self.name else filename,
            "Concepts": {name: con.minimise() for name, con in self._concepts.items()},
            "Relations": {}
        }

        for name, group in self._relations.items():

            concepts = []
            for relation in group:
                mini = relation.minimise()
                del mini["name"]
                concepts.append(mini)

            ontology["Relations"][name] = {
                "concepts": concepts
            }

        with open(os.path.join(folder, filename), "w") as handler:
            handler.write(json.dumps(ontology, indent=4))