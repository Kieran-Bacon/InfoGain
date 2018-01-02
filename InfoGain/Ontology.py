import json

from .Concept import Concept
from .Relation import Relation
from .Fact import Fact
from .Condition import Condition

class Ontology:
    """
    Ontology object, its represents and holds the concepts and relationships described in the ontology.
    """

    def __init__(self, name = None, filepath = None ):
        
        self.name = name                        # Simply idenfitication of the ontology, no functional use
        self._concepts = {}                     # Unique concept store
        self._relations = {}                    # Unique concept store
        self._facts = {}                        # key is relation, value list of facts for relation

        if filepath:

            # Extract the information from the input ontology file
            with open( filepath ) as ontologyFile:
                data = json.load( ontologyFile )

            conceptData = data["Concepts"]
            relationData = data["Relations"]
            factData = data["Facts"]

            # Concept creation
            def conceptCreation(name: str) -> None:
                """ Creates concept object for given name, if object does not already exist """
                
                if self.concept(name) is not None: return # Do nothing when concept exists

                rawConcept = conceptData[name] # Extract concept information from the input file

                concept = Concept(name, rawConcept.get("permable", False)) # Construct the concept object
                
                if "parents" in rawConcept:
                    for parentName in rawConcept["parents"]:
                        conceptCreation(parentName) # if exists: do nothing, else: create parent object
                        concept.addParent(self.concept(parentName)) # Collect parent and bind to current concept

                self.addConcept(concept) # Add concept to the ontology
            [conceptCreation(name) for name in conceptData.keys()] # Load in all concepts

            # Relation creation
            for name, rawRelation in relationData.items():

                # Collect the domain and ranges together from the ontology concepts
                domains = [self.concept(dom) for dom in rawRelation["domain"]]
                targets = [self.concept(tar) for tar in rawRelation["target"]]

                # Protect against referencing non existent concepts
                if any( [ con == None for con in domains + targets ] ):
                    raise ValueError( "Relation references unknown concept." )

                # Store the relation within the ontology
                self.addRelation( Relation( domains, name, targets ) )

            # Fact creation
            for rawFact in factData:

                # Collect ontology objects corresponding to the fact
                domain = self.concept(rawFact["domain"])
                relation = self.relation(rawFact["relation"])
                target = self.concept(rawFact["target"])

                if any([i == None for i in [domain,relation,target]]):
                    raise ValueError("Fact refers to unknown objects.")

                # Create fact object
                fact = Fact( domain, relation, target, rawFact["confidence"] )

                if "conditions" in rawFact:
                    # Add the conditions to the fact object
                    [fact.addCondition(condition(con["logic"], con["salience"])) for con in rawFact["conditions"]]

                # Add fact to ontology
                self.addFact(fact)

    def addConcept(self, concept: Concept) -> None:
        """
        Add concept object to ontology, overwrite previous concept if present. Identifies the relation ships 
        concepts parent objects are and becomes members to those relations if applicable.
        """
        self._concepts[concept.name] = concept
        [relation.subscribe(concept) for relation in self._relations.values()]

    def addRelation(self, relation: Relation):
        """ Adds a relation object to the ontology """
        self._relations[relation.name] = relation        # Store the relation, overwrite previous
        self._facts[relation.name] = []

    def addFact(self, fact: Fact):
        """ Adds a fact object to the ontology """
        self._facts[fact.relation.name].append(fact)
      
    def concept(self, conceptName: str) -> Concept:
        return self._concepts.get(conceptName, None)

    def relation(self, relationName: str) -> Relation:
        return self._relations.get(relationName, None)

    def facts(self, relationName: str) -> list:
        return self._facts[relationName]