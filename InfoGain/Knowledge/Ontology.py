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
            if "Name" in data: self.name = data["Name"]

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

                    if None in domains.union(targets): raise MissingConcept("Relation '" + name + 
                        "' references unknown concept.")

                    self.addRelation(Relation(domains, name, targets))

    def addConcept(self, concept: Concept) -> None:
        """ Add concept object to ontology, overwrite previous concept if present.
        Identifies the relation ships concepts parent objects are and becomes members to those
        relations if applicable. 
        
        Params:
            concept (Concept) - The concept to add
        """

        def link_concepts(first: Concept, second: Concept) -> None:
            """ Link the two concepts if applicable 
            
            Params:
                first (Concept) - Concept one 
                second (Concept - Concept two
            """
            if isinstance(second, str):
                second = self.concept(second)
                if not second:
                    return

            # Link if first is the parent of second
            if first in second.parents or second in first.children:
                second.parents.discard(first)
                second.parents.add(first)

                first.children.discard(second)
                first.children.add(second)

            # Link if first is the child of second
            if first in second.children or second in first.parents:
                second.children.discard(first)
                second.children.add(first)

                first.parents.discard(second)
                first.parents.add(second)

        # Link concepts in the ontology that may link to the concept
        [link_concepts(concept, ontology_concept) for ontology_concept in self._concepts.values()]

        # Link concept to the ontology's concepts
        [link_concepts(concept, parent) for parent in concept.parents]
        [link_concepts(concept, child) for child in concept.children]
                
        # Save concept
        self._concepts[concept.name] = concept
        [inst.subscribe(concept) for relation in self._relations.values() for inst in relation]

    def addRelation(self, relation: Relation) -> None:
        """ Add a new relation object to the ontology, correctly link the relation concepts to the 
        ontology.
        
        Params:
            relation (Relation) - The relation object to add to the ontology
        """
 
        # Ensure the domain concepts are correctly linked with the relation
        for con in relation.domains:
            if isinstance(con, str):
                con = self.concept(con)
                if con is None:
                    raise MissingConcept("Newly added relation '" + relation.name + 
                        "' references concepts not in ontology")
                else:
                    relation.domains.remove(con)
                    relation.domains.add(con)

        # Ensure the target concepts are correctly linked with the relation
        for con in relation.targets:
            if isinstance(con, str):
                con = self.concept(con)
                if con is None:
                    raise MissingConcept("Newly added relation '" + relation.name + 
                        "' references concepts not in ontology")
                else:
                    relation.targets.remove(con)
                    relation.targets.add(con)


        # Add the relationship to the ontology store
        pairing = self._relations.get(relation.name, set())
        pairing.add(relation)
        self._relations[relation.name] = pairing

    def concept(self, conceptName: str) -> Concept:
        """ Collect the ontology concept with the name given, or None """
        return self._concepts.get(conceptName, None)

    def concepts(self) -> [Concept]:
        """ Return a list of concepts found within the ontology, order is non deterministic """
        return list(self._concepts.values())

    def relation(self, relationName: str) -> Relation:
        """ Collect the relation objects for name given, or None """
        collection = self._relations.get(relationName, None)
        return collection

    def relations(self, keys=False) -> [str]:
        """ Return the ontology relations or the names of all the relations 
        
        Params:
            keys (bool) - Toggle for the names of the relations or the relations themselves
        
        Returns:
            [str] - A list of names of the relations or a list of relation objects
        """
        if keys: return self._relations.keys()
        return list(self._relations.values())

    def findRelations(self, domain: str, target: str) -> [Relation]:
        """ Return a list of relations that could be formed between the domain and the target 
        objects. Yield the relations.
        
        Params:
            domain (Concept) - A concept that needs to match with the domain of potential relations
            target (Concept) - A concept that needs to match with the target of potential relations
        """
        dom, tar = self.concept(domain), self.concept(target)
        if None in (dom, tar):
            raise Exception("Invalid concepts provided when looking for relations")

        for parings in self.relations():
            for relation in parings:
                if relation.between(dom, tar):
                    yield relation

    def clone(self):
        """ Create a new ontology object that is a deep copy of this ontology instance 
        
        Returns:
            clone (Ontology) - A deep copy of this ontology object
        """

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
        """ Save the file to the current working directory or the filename provided
        
        Params:
            folder (str) - The directory destination of the saved file
            filename (str) - The name to be given to the saved file
        """

        import os, uuid

        if filename is None and self.name is None: filename = uuid.uuid4().hex
        if self.name and not filename: filename = self.name
            
        ontology = {
            "Name": self.name if self.name else filename,
            "Concepts": {},
            "Relations": {}
        }

        for name, concept in self._concepts.items():
            mini = concept.minimise()
            del mini["name"]
            ontology["Concepts"][name] = mini

        for name, group in self._relations.items():

            concepts = []
            for relation in group:
                mini = relation.minimise()
                del mini["name"]
                concepts.append(mini)

            ontology["Relations"][name] = {
                "concepts": concepts
            }

        with open(os.path.abspath(os.path.join(folder, filename)), "w") as handler:
            handler.write(json.dumps(ontology, indent=4))