from . import ConsistencyError
from ..knowledge import Ontology, Concept, Relation, Rule
from .instance import ConceptInstance, RelationInstance
from .evalrule import EvalRule
from .evaltrees import EvalTreeFactory

import logging
log = logging.getLogger(__name__)

class InferenceEngine(Ontology):
    """ Through a collection of knowledge, infer information that is consitent with what is known
    stating confidence in the inference as we produce it """

    def __init__(self, name:str = None, filepath:str=None, ontology:Ontology=None):

        Ontology.__init__(self, name=name, filepath=filepath)
        self._conceptInstances = {}

        if ontology:
            ont = ontology.clone()
            self.name = name if name else ont.name
            # Load in concepts
            for concept in ont._concepts.values(): self.addConcept(concept)
            # Load in the relations
            for relation in ont._relations.values(): self.addRelation(relation)

        if filepath:
            Ontology.__init__(name, filepath=filepath)

    def addConcept(self, concept: Concept) -> None:
        Ontology.addConcept(self, concept)  # Call the original add concept function

        self._conceptInstances[concept.name] = []
        if concept.category == Concept.STATIC:
            self._conceptInstances[concept.name].append(ConceptInstance(concept))

    def addRelation(self, relation: Relation):
        Ontology.addRelation(self, relation)  # Call the original add relation function

        evalRules = []
        for rule in relation.rules():
            # Update all the rules within the relation with evalable rules
            minimsied = rule.minimise()
            minimsied["domains"] = {self.concept(con) for con in minimsied["domains"]}
            minimsied["targets"] = {self.concept(con) for con in minimsied["targets"]}
            minimsied["ontology"] = self
            evalRules.append(EvalRule(**minimsied))

        # Unpackage the rules of the ontology, generate eval rules to represent them
        relation.assignRules(evalRules)

    def instances(self, concept_name: str, expand: bool = False) -> [ConceptInstance]:

        if expand:
            concept = self.concept(concept_name)
            expanded = Concept.expandConceptSet({concept})
            return [inst for con in expanded for inst in self._conceptInstances.get(con.name, [])]

        return self._conceptInstances.get(concept_name, [])

    def addInstance(self, concept_instance: ConceptInstance) -> None:
        if concept_instance.name in self._concepts:
            self.addConcept(concept_instance.concept)  # Add the concept the instance is associated with

            # Assign this instance - overwrite a concept instance if it has been generated during adding
            self._conceptInstances[concept_instance.name] = [concept_instance]

        else:
            # The concept exists 
            if concept_instance.category == Concept.STATIC:
                raise ConsistencyError("Attempting to add instance for {} despite concept category".format(concept_instance.name))

            self._conceptInstances[concept_instance.name].append(concept_instance)

    def inferRelation(self, domain: str, relation: str, target: str):
        """ Determine the confidence of a relation between entities """

        if isinstance(domain, str):
            domain = self.instances(domain)[0]
            target = self.instances(target)[0]

        relation = self.relation(relation)  # Collect the relation

        log.info("Infering relation '{} {} {}' - {} rules found for relation instance".format( domain, relation.name, target, len(relation.rules(domain, target))))

        confidence = 0
        for rule in relation.rules(domain, target):
            confidence += rule.eval(domain, target)

        return confidence