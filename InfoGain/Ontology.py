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

        # Simply idenfitication of the ontology, no functional use
        self.name = name
        self._concepts = {}                     # Unique concept store
        self._relations = {}                    # Unique relation store
        # key is relation, value list of facts for relation
        self._facts = {}

        if filepath:

            # Extract the information from the input ontology file
            with open(filepath) as ontologyFile:
                data = json.load(ontologyFile)

            # Concept creation
            def conceptCreation(name: str) -> None:
                """ Creates concept object for given name, if object does not already exist """
                if self.concept(name) is not None:
                    return  # Do nothing as the concept exists

                # Extract concept information from the input file
                conceptData = data["Concepts"][name]
                # Construct the concept object
                concept = Concept(name, conceptData)

                if "parents" in conceptData:
                    for parentName in conceptData["parents"]:
                        # if exists: do nothing, else: create parent object
                        conceptCreation(parentName)
                        parent = self.concept(parentName)
                        parent.addChild(concept)
                        concept.addParent(parent)

                self.addConcept(concept)  # Add concept to the ontology

            if "Concepts" in data:
                # Load in all concepts
                [conceptCreation(name) for name in data["Concepts"].keys()]

            # Relation creation
            if "Relations" in data:
                for name, rawRelation in data["Relations"].items():

                    rawDomains = rawRelation["domain"]
                    rawTargets = rawRelation["target"]

                    if not rawRelation.get("sets",False):
                        rawDomains, rawTargets = [rawDomains], [rawTargets]

                    # Relation contains sets of domain, target pairings
                    
                    domains = [{self.concept(dom) for dom in domset} 
                        for domset in rawDomains]
                    targets = [{self.concept(tar) for tar in tarset}
                        for tarset in rawTargets]

                    if any([con is None for group in domains+targets for con in group]):
                        raise MissingConcept("Relation '"+name+"' references unknown concept.")

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
                    fact = Fact(domain, relation, target,
                                rawFact["confidence"])

                    if "conditions" in rawFact:
                        # Add the conditions to the fact object
                        [fact.addCondition(Condition(con["logic"], con["salience"]))
                         for con in rawFact["conditions"]]

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

    def concepts(self) -> [Concept]:
        """ Return a list of concepts found within the ontology, order is non deterministic """
        return list(self._concepts.values())

    def relation(self, relationName: str) -> Relation:
        return self._relations.get(relationName, None)

    def relations(self) -> [str]:
        return list(self._relations.values())

    def findRelations(self, domain: str, target: str):
        """ Return a list of relations that could be formed between the domain and the target """
        dom, tar = self.concept(domain), self.concept(target)
        if None in (dom, tar): raise Exception("Invalid concepts provided when looking for relations")

        for relation in self.relations():
            if relation.hasDomain(dom) and relation.hasTarget(tar):
                yield relation

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

        return ontologyClone

    def conceptText(self) -> {str: [str]}:
        """ Return a map from concept text repr into the concept name """

        # Concept names are also repr
        ontTextRepr = {name: name for name in self._concepts.keys()}

        for concept in self.concepts():
            for text in concept.textRepr():

                #TODO: Either handle overlapping reprs or ensure that it doesn't happen

                ontTextRepr[text] = concept.name

        return ontTextRepr

    def save(self, filename=None) -> None:
        """ Save the file to the current working directory or the filename provided """

        if filename is None:
            filename = "./" + self.name + ".json"

        concepts = {name: concept.minimise() for name, concept in self._concepts.items()}
        relations = {name: relation.minimise() for name, relation in self._relations.items()}

        # TODO:Add facts
        ontology = {"Concepts": concepts, "Relations": relations}

        if not self.name is None: ontology["name"] = self.name

        with open(filename, "w") as handler:
            handler.write(json.dumps(ontology, indent=4))

class MissingConcept(Exception):
    pass