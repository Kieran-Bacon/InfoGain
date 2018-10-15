from ..exceptions import ConsistencyError
from ..artefact import Document
from ..knowledge import Ontology, Concept, Instance, Relation, Rule
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
        """ Add a concept into the engine ontology

        Params:
            concept (Concept): The concept object to be added
        """
        Ontology.addConcept(self, concept)  # Call the original add concept function

        if concept.category is Concept.ABSTRACT: return

        self._conceptInstances[concept.name] = []
        if concept.category is Concept.STATIC:
            self._conceptInstances[concept.name].append(concept.instance())

    def addRelation(self, relation: Relation):
        """ Add a relationship into the engine - convert any rules within the relations to
        evaluable rules according to the engine

        Params:
            relation (Relation): The relation to be added

        Raises:
            IncorrectLogic: A rule within the relation has malformed logic
        """

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
                    rule = EvalRule(domain, relation.name, target, point.probability*100, supporting=point.prediction)
                    rule.assignOntology(self)
                    relation.addRule(rule)
                else:
                    log.debug("Datapoint's relation {} missed during adding of world knowledge".format(point.relation))        

    def inferRelation(self, domain: Instance, relation: (str, Relation), target: Instance):
        """ Determine the confidence of a relation between entities 
        
        Params:
            domain (ConceptInstance): A concept instance which is a domain of the relation
            relation (str/Relation): The string identifier of a relation, or the relation itself
            target (ConceptInstance): A concept instance of which is a target of the relation
        
        Returns:
            float: The certainty of a relation which falls between the range(0, 100)
        """

        if isinstance(relation, (str)): relation = self.relation(relation)
        domConcept, tarConcept = self.concept(domain.concept), self.concept(target.concept)

        if None is (domConcept or tarConcept): raise Exception("Cannot infer relation between concepts unknown to the engine")

        log.info("Infering relation '{} {} {}' - {} rules found for relation instance".format(
            domain, relation.name, target, len(relation.rules(domConcept, tarConcept))))


        confidence = 0
        for rule in relation.rules(domConcept, tarConcept):
            confidence += rule.eval(domain, target)

        return confidence