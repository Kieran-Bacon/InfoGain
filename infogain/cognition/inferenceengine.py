from ..exceptions import ConsistencyError
from ..artefact import Document
from ..knowledge import Ontology, Concept, Instance, Relation, Rule

from .evalrelation import EvalRelation
from .evalrule import EvalRule
from .evaltrees import EvalTreeFactory

import logging
log = logging.getLogger(__name__)

class InferenceEngine(Ontology):
    """ Through a collection of knowledge, infer information that is consitent with what is known
    stating confidence in the inference as we produce it """

    def __init__(self, name:str = None, filepath:str=None, ontology:Ontology=None):

        Ontology.__init__(self, name=name, filepath=filepath)
        self._conceptInstances = {}  # Links concepts to their instances
        self._instances = {}  # stores instances

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
        """ Add a concept into the engine ontology

        Params:
            concept (Concept): The concept object to be added
        """
        Ontology.addConcept(self, concept)  # Call the original add concept function

        if concept.category is Concept.ABSTRACT: return

        self._conceptInstances[concept.name] = []
        if concept.category is Concept.STATIC:
            instance = concept.instance()
            self._conceptInstances[concept.name].append(instance)
            self._instances[concept.name] = instance

    def addRelation(self, relation: Relation):
        """ Add a relationship into the engine - convert any rules within the relations to
        evaluable rules according to the engine

        Params:
            relation (Relation): The relation to be added

        Raises:
            IncorrectLogic: A rule within the relation has malformed logic
        """
        evalRelation = EvalRelation.fromRelation(relation, self)
        Ontology.addRelation(self, evalRelation)
        return evalRelation

    def relation(self, relation: (str, Relation)):
        if isinstance(relation, Relation): relation = relation.name
        return Ontology.relation(self, relation)

    def addInstance(self, concept_instance: Instance) -> None:
        """ Add a concept instance - Only possible for dynamic concepts

        Params:
            concept_instance (ConceptInstance): The instance object to be added

        Raises:
            ConsistencyError: In the event that the concept is not already apart of the engine
            TypeError: In the event that the concept is not suitable for additional instances
        """

        concept = self.concept(concept_instance.concept)
        if concept is None: raise ConsistencyError("{} is not an concept within the engine - Cannot add instance for missing concept".format(concept_instance.concept)) 
        if concept.category is Concept.ABSTRACT or concept.category is Concept.STATIC: raise TypeError("{} is not suitable for additional instances. Its category needs to be set to dynamic".format(concept.name))

        self._conceptInstances[concept.name].append(concept_instance)
        self._instances[concept_instance.name] = concept_instance

    def instance(self, instance_name: str) -> Instance:
        """ Collect an instance with the provided name or return None in the event that no instance exists with that
        name

        Params:
            instance_name (str): The instance name

        Returns:
            Instance: The instance object with the same name
            None: The instance could not be found
        """
        return self._instances.get(instance_name)

    def instances(self, concept_name: str, descendants: bool = False) -> [Instance]:
        """ Collect the instances for a concept identifier. If the concept is static then only its 
        single instance shall be returned. Or all the instances for a concept and its children.

        Params:
            concept_name (str): The concept idenfitier
            descendants (bool): Along with the concept gather the descendant concept's instances

        Returns:
            ConceptInstances: A ConceptInstance or a list of concept instances
        """

        concept = self.concept(concept_name)

        if descendants:
            expanded = Concept.expandConceptSet({concept})
            return [inst for con in expanded for inst in self._conceptInstances.get(con.name, [])]

        if concept.category is Concept.ABSTRACT:
            log.warning(
                "Attempting to collect instances for an Abstract concept" +
                " - Mistake to call instances on {}".format(concept_name))
            return []

        if concept.category is Concept.STATIC:
            return concept.instance() # Singlton - will return stored instance  

        return self._conceptInstances.get(concept_name, [])

    def addWorldKnowledge(self, documents: [Document]) -> None:
        """ Add world knowledge into the inference engine via document datapoints, unmatched datapoints
        are ignored.

        Params:
            documents ([Document]): A list of document objects each with datapoints (hopefully)
        """

        for document in documents:
            for point in document.datapoints():
                if point.prediction == 0: continue  # No information

                domain = self.concept(point.domain["concept"])
                relation = self.relation(point.relation)
                target = self.concept(point.target["concept"])

                if relation:
                    rule = EvalRule(domain, target, point.probability*100, point.prediction == point.POSITIVE)
                    rule.assignOntology(self)
                    relation.addRule(rule)
                else:
                    log.debug("Datapoint's relation {} missed during adding of world knowledge".format(point.relation))

        self.reset()        

    def inferRelation(self, domain: Instance, relation: (str, Relation), target: Instance, *, evaluate_conditions=True) -> float:
        """ Determine the confidence of a relation between entities 
        
        Params:
            domain (ConceptInstance): A concept instance which is a domain of the relation
            relation (str/Relation): The string identifier of a relation, or the relation itself
            target (ConceptInstance): A concept instance of which is a target of the relation
        
        Returns:
            float: The certainty of a relation which falls between the range(0, 100)
        """

        if isinstance(relation, (str, Relation)): relation = self.relation(relation)
        domConcept, tarConcept = self.concept(domain.concept), self.concept(target.concept)

        if None is (domConcept or tarConcept): raise Exception("Cannot infer relation between concepts unknown to the engine")

        log.info("Infering relation '{} {} {}' - {} rules found for relation instance".format(
            domain, relation.name, target, len(relation.rules(domain, target))))

        confidence, scepticism = 1.0, 1.0
        for rule in relation.rules(domain, target):
            log.debug("Rule: {}".format(rule))
            if not evaluate_conditions and rule.hasConditions(domain, target):
                continue  # Avoid condition rules

            ruleValue = (1.0 - rule.eval(domain, target)/100)
            log.debug(rule.supporting)
            if rule.supporting: confidence *= ruleValue
            else:               scepticism *= ruleValue

        return ((1.0 - confidence) - (1.0 - scepticism))*100

    def reset(self):
        """ Clean up any information collected during inference. """
        for relation in self._relations.values():
            for rule in relation.rules():
                rule.reset()