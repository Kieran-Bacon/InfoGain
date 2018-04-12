import json

from .Concept import Concept
from .Relation import Relation
from .Fact import Fact
from .Condition import Condition


class Ontology:
    """
    Ontology object, its represents and holds the concepts and relationships described in the ontology.
    """

    def __init__(self, name=None, filepath=None):

        self.name = name                        # Simply idenfitication of the ontology, no functional use
        self._concepts = {}                     # Unique concept store
        self._relations = {}                    # Unique relation store
        self._facts = {}                        # key is relation, value list of facts for relation

        if filepath:

            # Extract the information from the input ontology file
            with open(filepath) as ontologyFile:
                data = json.load(ontologyFile)

            # Concept creation
            def conceptCreation(name: str) -> None:
                """ Creates concept object for given name, if object does not already exist """
                if self.concept(name) is not None:
                    return  # Do nothing as the concept exists

                conceptData = data["Concepts"][name]  # Extract concept information from the input file
                concept = Concept(name, conceptData)  # Construct the concept object

                if "parents" in conceptData:
                    for parentName in conceptData["parents"]:
                        conceptCreation(parentName)  # if exists: do nothing, else: create parent object
                        parent = self.concept(parentName)
                        parent.addChild(concept)
                        concept.addParent(parent)

                self.addConcept(concept)  # Add concept to the ontology

            if "Concepts" in data:
                [conceptCreation(name) for name in data["Concepts"].keys()]  # Load in all concepts

            # Relation creation
            if "Relations" in data:
                for name, rawRelation in data["Relations"].items():

                    # Collect the domain and ranges together from the ontology concepts
                    domains = {self.concept(dom) for dom in rawRelation["domain"]}
                    targets = {self.concept(tar) for tar in rawRelation["target"]}

                    # Protect against referencing non existent concepts
                    if any([con is None for con in domains.union(targets)]):
                        raise ValueError("Relation references unknown concept.")

                    # Store the relation within the ontology
                    self.addRelation(Relation(domains, name, targets))

            # Fact creation
            if "Facts" in data:
                for rawFact in data["Facts"]:

                    # Collect ontology objects corresponding to the fact
                    domain = self.concept(rawFact["domain"])
                    relation = self.relation(rawFact["relation"])
                    target = self.concept(rawFact["target"])

                    if any([i is None for i in [domain, relation, target]]):
                        raise ValueError("Fact refers to unknown objects.")

                    # Create fact object
                    fact = Fact(domain, relation, target, rawFact["confidence"])

                    if "conditions" in rawFact:
                        # Add the conditions to the fact object
                        [fact.addCondition(Condition(con["logic"], con["salience"])) for con in rawFact["conditions"]]

                    # Add fact to ontology
                    self.addFact(fact)

    def addConcept(self, concept: Concept) -> None:
        """ Add concept object to ontology, overwrite previous concept if present.
        Identifies the relation ships concepts parent objects are and becomes members to those
        relations if applicable. """
        self._concepts[concept.name] = concept
        [relation.subscribe(concept) for relation in self._relations.values()]

    def addRelation(self, relation: Relation) -> None:
        """ Adds a relation object to the ontology """
        self._relations[relation.name] = relation        # Store the relation, overwrite previous
        self._facts[relation.name] = []

    def addFact(self, fact: Fact) -> None:
        """ Adds a fact object to the ontology """
        self._facts[fact.relation.name].append(fact)

    def concept(self, conceptName: str) -> Concept:
        return self._concepts.get(conceptName, None)

    def concepts(self) -> [str]:
        return list(self._concepts.values())

    def relation(self, relationName: str) -> Relation:
        return self._relations.get(relationName, None)

    def relations(self) -> [str]:
        return list(self._relations.values())

    def facts(self, relationName: str) -> list:
        return self._facts[relationName]

    def clone(self):
        """ Create a new ontology object that is a deep copy of this ontology instance """

        ontologyClone = Ontology(self.name)
        
        # Clone concepts
        [ontologyClone.addConcept(con.clone()) for con in self.concepts()]

        for concept in ontologyClone.concepts():
            # Connect the cloned concepts with their new cloned parents/children and make valid
            concept.parents = {ontologyClone.concept(con) for con in concept.parents}
            concept.children = {ontologyClone.concept(con) for con in concept.children}
            concept._state = "valid"

        # Clone relationships
        for relation in self._relations.values():
            domains = {ontologyClone.concept(dom.name) for dom in relation.domains()}
            targets = {ontologyClone.concept(tar.name) for tar in relation.targets()}
            ontologyClone.addRelation(Relation(domains, relation.name, targets))

        # Clone facts
        #TODO: Clone facts, min: switch for logging function.
        print("Warning :: Clone does not close facts")

        return ontologyClone

    def conceptText(self) -> {str: [str]}:
        """ Return a map from concept text repr into the concept name """

        ontTextRepr = {name: [name] for name in self._concepts.keys()}  # Concept names are also repr

        for concept in self.concepts():
            for text in concept.textRepr():
                if not text in ontTextRepr:
                    ontTextRepr[text] = []
                
                ontTextRepr[text].append(concept.name)

        return ontTextRepr


    def save(self, filename=None) -> None:
        """ Save the file to the current working directory or the filename provided """

        if filename is None:
            filename = "./" + self.name + ".json"

        concepts = {}
        for name, concept in self._concepts.items():
            concepts[name] = {"parents": [name for name in concept.parents]}

        relations = {}
        for relname, relation in self._relations.items():
            relations[relname] = {"domain": [con.name for con in relation.domains()], "target": [con.name for con in relation.targets()]}

        # TODO:Add facts
        ontology = {"Concepts": concepts, "Relations": relations}

        with open(filename, "w") as handler:
            handler.write(json.dumps(ontology, indent=4))
