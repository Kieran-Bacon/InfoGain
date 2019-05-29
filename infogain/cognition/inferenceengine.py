import collections
import weakref

from ..exceptions import ConsistencyError
from ..artefact import Document
from ..knowledge.concept import Concept, ConceptSet
from ..knowledge import Instance, Relation, Rule
from ..knowledge.ontology import Ontology, OntologyConcepts, OntologyRelations

from .evalrelation import EvalRelation
from .evalrule import EvalRule
from .evaltrees import EvalTreeFactory

import logging
log = logging.getLogger(__name__)

class InferenceEngine(Ontology):
    """ Running on top of an ontology, an interfence engine can infer the confidence in ontology relationships by
    examining the current world view described by the ontology's member components.

    Params:
        name (str) = None: The name given to describe this collection of knowledge
        ontology (Ontology) = None: A starting point of knowledge, a base in which is infer

    Attr:
        name (str): The name of the engine's collection of knowledg
    """

    def __init__(self, name: str = None, ontology: Ontology = None):

        # Simply identification of the ontology, no functional use
        self.name = name

        # The internal storage containers
        self._concepts = InferenceEngineConcepts(weakref.proxy(self))
        self._instances = InferenceEngineInstances(weakref.proxy(self))
        self._relations = InferenceEngineRelations(weakref.proxy(self))

        if ontology:
            # Add each of the items of the provided ontology into the engine - clone elements to avoid coupling issues
            if self.name is None and ontology.name is not None:
                self.name = ontology.name

            for concept in ontology.concepts():
                self.concepts.add(concept.clone())

            for relation in ontology.relations():
                self.relations.add(relation.clone())

    @property
    def instances(self) -> OntologyConcepts:
        """ Inference engine instances container """
        return self._instances

    def addWorldKnowledge(self, documents: [Document]) -> None:
        """ Add world knowledge into the inference engine via document datapoints, unmatched datapoints
        are ignored.

        Params:
            documents ([Document]): A list of document objects each with datapoints (hopefully)
        """

        for document in documents:
            for point in document.datapoints():
                if point.prediction == 0: continue  # No information

                domain = self.concepts(point.domain["concept"])
                relation = self.relations(point.relation)
                target = self.concepts(point.target["concept"])

                if relation:
                    rule = EvalRule(
                        domain,
                        target,
                        point.probability*100,
                        supporting = point.prediction == point.POSITIVE,
                        ontology=self
                    )
                    relation.addRule(rule)
                else:
                    log.debug("Datapoint's relation {} missed during adding of world knowledge".format(point.relation))

        self.reset()

    def inferRelation(self, domain: Instance, relation: str, target: Instance, *, evaluate_conditions=True) -> float:
        """ Determine the confidence of a relation between entities

        Params:
            domain (ConceptInstance): A concept instance which is a domain of the relation
            relation (str/Relation): The string identifier of a relation, or the relation itself
            target (ConceptInstance): A concept instance of which is a target of the relation

        Returns:
            float: The certainty of a relation which falls between the range(0, 100)
        """

        if isinstance(relation, (str, Relation)): relation = self.relations(relation)
        domConcept, tarConcept = self.concepts(domain.concept), self.concepts(target.concept)

        if None is (domConcept or tarConcept):
            raise Exception("Cannot infer relation between concepts unknown to the engine")

        log.info("Infering relation '{} {} {}' - {} rules found for relation instance".format(
            domain, relation.name, target, len(relation.rules(domain, target))))

        rulePositive, ruleNegative = False, False
        confidence, scepticism = 1.0, 1.0
        for rule in relation.rules(domain, target):
            log.debug("Rule: {}".format(rule))
            if not evaluate_conditions and rule.hasConditions(domain, target):
                continue  # Avoid condition rules

            ruleValue = (1.0 - rule.eval(domain, target)/100)
            if rule.supporting:
                rulePositive = True
                confidence *= ruleValue
            else:
                ruleNegative = True
                scepticism *= ruleValue

        # If the confidence has not been editted then we don't want to consider it in the function
        # equally if the scepticism has not been set
        # we don't want to do it

        if rulePositive:
            return ((1.0 - confidence) * (scepticism))*100
        elif ruleNegative:
            return scepticism*100
        else:
            None  # There is nothing to suggest any answer - don't suggest that it is entirely negative

    def reset(self):
        """ Clean up any information collected during inference. """
        for relation in self._relations.values():
            for rule in relation.rules():
                rule.reset()

class InferenceEngineConcepts(OntologyConcepts):

    def add(self, concept: Concept) -> None:
        """ Add a concept into the engine knowledge base and extend the containter for instances

        Params:
            concept (Concept): The concept to be added
        """

        super().add(concept)

        if concept.category is Concept.STATIC:
            self._owner.instances().add(concept.instance())

    def remove(self, concept: Concept) -> None:
        super().remove(concept)

        self._owner.instances().remove(concept)

class InferenceEngineInstances(collections.abc.MutableMapping):

    def __init__(self, owner: weakref.ProxyType):
        self._owner = owner
        self._elements = {}
        self._conceptMapping = collections.defaultdict(set)

    def __len__(self): return len(self._elements)

    def __setitem__(self, name: str, instance: Instance):
        """ Add a concept instance - Only possible for dynamic concepts

        Params:
            concept_instance (ConceptInstance): The instance object to be added

        Raises:
            ConsistencyError: In the event that the concept is not already apart of the engine
            TypeError: In the event that the concept is not suitable for additional instances
        """

        # Ensure that the owning concept is a member of the engine
        concept = self._owner.concepts(instance.concept)
        if concept is None:
            raise ConsistencyError(
                "{} is not an concept within the engine - it's instance cannot be added".format(repr(instance))
            )

        # Ensure that the owning concept is capable of having instances
        if concept.category is (Concept.ABSTRACT or Concept.STATIC):
            raise TypeError("{} is not suitable for additional instances.".format(concept.name))

        self._elements[instance.name] = instance
        self._conceptMapping[instance.concept].add(instance)
        
    def __getitem__(self, name: str): return self._elements[name]

    def __delitem__(self, name: str):
        """ Remove an instance by its given name from the container """

        instance = self._elements[name]
        if instance.concept is Concept.STATIC and instance.concept in self._owner.concepts():
            raise ConsistencyError("You cannot remove the static instance of a concept - You must remove the concept")
        del self._elements[name]
        self._conceptMapping[instance.concept].remove(instance)
        if not self._conceptMapping[instance.concept]: del self._conceptMapping[instance.concept]
    
    def __iter__(self): return iter(self._elements)

    def __call__(self, concept: Concept, descendants: bool = False)  -> (Instance, {Instance}):
        """ Collect the instance who's namee has been specified, or collect the instances for a concept identifier. If
        descendants is true, then in the event that a concept is passed, all instances of descendant concepts shall also
        be returned.

        Params:
            concept (str/Concept): The name of the instance to be returned, or the concept idenfitier
            descendants (bool): Along with the concept gather the descendant concept's instances

        Returns:
            ConceptInstances: A ConceptInstance or a list of concept instances
        """
        
        if isinstance(concept, str):
            return self.get(concept)  # Return the instance with the given name or None

        elif isinstance(concept, Concept):

            if descendants:
                return {inst for con in ConceptSet({concept}).expanded() for inst in self._conceptMapping.get(con)}

            if concept.category is Concept.ABSTRACT:
                log.warning("Cannot collect instances of an Abstract concept {}".format(concept))
                return set()

            return self._conceptMapping.get(concept, set())
        else:
            raise TypeError("Incorrect type passed to Instance Container call method")

    def add(self, instance: Instance) -> None:
        """ Add a concept instance - Only possible for dynamic concepts

        Params:
            concept_instance (ConceptInstance): The instance object to be added

        Raises:
            ConsistencyError: In the event that the concept is not already apart of the engine
            TypeError: In the event that the concept is not suitable for additional instances
        """

        concept = self._owner.concepts(instance.concept)
        if concept is None:
            raise ConsistencyError(
                "{} is not an concept within the engine - Invalid addition of instance".format(repr(instance))
            )
        if concept.category is (concept.ABSTRACT or concept.STATIC):
            raise TypeError("{} is not suitable for additional instances.".format(concept.name))

        self._conceptMapping[concept].add(instance)
        self._elements[instance.name] = instance

class InferenceEngineRelations(OntologyRelations):

    def __call__(self, relation: Relation) -> Relation:
        """ Collect the member relationship with the given name in the ontology. If relation passed, return relation
        from ontology that has the same name

        Params:
            relation (str/Relation): The name of the relation ship to collect, or a relation object who's name is to be
                collected

        Returns:
            Relation: The relation object present within the engine
        """
        if isinstance(relation, Relation): relation = relation.name
        return super().__getitem__(relation)

    def add(self, relation: Relation):
        """ Add a relationship into the engine - convert any rules within the relations to
        evaluable rules according to the engine

        Params:
            relation (Relation): The relation to be added

        Raises:
            IncorrectLogic: A rule within the relation has malformed logic
        """
        return super().add(EvalRelation.fromRelation(relation))