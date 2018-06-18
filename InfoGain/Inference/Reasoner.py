from ..Documents import Document
from ..Knowledge import Ontology, Concept, Relation, Rule, Fact

class Reasoner(Ontology):
    """ Perform cognitive reasoning on within the scope of a domain and infere different relationships """

    def __init__(self, name = None, filepath = None, ontology: Ontology=None):
        Ontology.__init__(self, name, filepath)  # Run the initialisation process of the ontology

        if ontology:
            # An ontology object was provided, clone it and extract duplicated information
            clone = ontology.clone()
            self.name = clone.name if not name else name 
            self._concepts = clone._concepts
            self._relations = clone._relations

    def knowledge(self, documents: {Document} = set(), facts: {Fact} = set()) -> None:
        pass

    def addInstance(self, instance: Concept) -> None:
        """ Add a concept instance into the reasoning engine """
        pass

    def evaluateRelation(self, domain: Concept, relation: Relation, target: Concept) -> Relation:
        pass