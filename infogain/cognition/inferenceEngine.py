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

        self._conceptInstances = {}

        if ontology:
            Ontology.__init__(self)
            ont = ontology.clone()
            self.name = name if name else ont.name

            # Load in concepts
            self._concepts = ont._concepts
            for name, concept in self._concepts.items():
                if concept.category == Concept.STATIC:
                    # Create concept instances for static concepts
                    self._conceptInstances[name] = [ConceptInstance(concept)]

            # Load in the relations
            self._relations = ont._relations
            for name, relation in self._relations.items():

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

        if filepath:
            Ontology.__init__(name, filepath=filepath)

    def instances(self, concept_name: str, expand: bool = False) -> [ConceptInstance]:

        if expand:
            concept = self.concept(concept_name)
            expanded = Concept.expandConceptSet({concept})
            return [inst for con in expanded for inst in self._conceptInstances.get(con.name, [])]

        return self._conceptInstances.get(concept_name, [])


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