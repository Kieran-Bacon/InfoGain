import itertools

from ..knowledge import Ontology, Concept, Rule
from .instance import ConceptInstance
from .evaltrees import EvalTreeFactory, EvalTree

import logging
log = logging.getLogger(__name__)

class EvalRule(Rule):

    def __init__(self, domains: {Concept}, relation: str, targets: {Concept}, confidence: float, conditions: [dict] = [], ontology: Ontology = None):
        Rule.__init__(self, domains, relation, targets, confidence, conditions)
        if ontology: self.assignOntology(ontology)

    def assignOntology(self, ontology: Ontology) -> None:
        """ Assign the ontology object to the rule and link the correct variables """
        self.engine = ontology

        self.domains = {self.engine.concept(con) for con in self.domains if isinstance(con, str)}.union(self.domains)
        self.targets = {self.engine.concept(con) for con in self.targets if isinstance(con, str)}.union(self.targets)

        self._factory = EvalTreeFactory(self.engine)
        self._evaluatedConfidences = {} 
        self._conditionTrees = [self._factory.constructTree(cond["logic"]) for cond in self._conditions]

        self._parameters = {}
        for tree in self._conditionTrees:
            for param in tree.parameters():
                self._parameters[param] = EvalTreeFactory.paramToConcept(param)


        self._parameters = {param for tree in self._conditionTrees for param in tree.parameters()}.difference({"%", "@"})

    def eval(self, domain: ConceptInstance, target: ConceptInstance):
        """ Evaluate all the scenarios of a particular relation instance and determine the confidence
        of the relation """

        if domain not in self.domains and target not in self.targets:
            log.debug("Rule doesn't apply to the paring, returning None")
            return 0  # Return 0 as the rule doesn't support the pair provided

        pairing_key = "-".join([str(domain), str(target)])  # Generate the key for this pairing

        if pairing_key in self._evaluatedConfidences:
            log.debug("Evaluating rule for {} {} {} - returning previous calculated value {}".format(domain, self.relation, target, self._evaluatedConfidences[pairing_key]))
            return self._evaluatedConfidences[pairing_key]  # Returned previously evaluted score

        log.debug("Evaluating rule for {} {} {}".format(domain, self.relation, target))

        ruleConfidence = 1.0
        params = list(self._parameters)
        instances = []
        for param in params:
            conceptName, expand = EvalTreeFactory.paramToConcept(param)
            instances.append(self.engine.instances(conceptName, expand))

        for scenario_instances in itertools.product(*instances):

            scenario = {param: scenario_instances[i] for i, param in enumerate(params)}
            scenario["%"] = domain
            scenario["@"] = target

            log.debug("Evaluating rule scenario - {}".format({k: v.name for k,v in scenario.items()}))

            confidence = self.evalScenario(scenario)/100

            ruleConfidence *= (1.0-confidence)
            if ruleConfidence < 0:
                return 0

        self._evaluatedConfidences[pairing_key] = (1.0 - ruleConfidence)*100
        return (1.0 - ruleConfidence)*100

    def evalScenario(self, scenario: dict) -> float:

        scenarioConfidence = 0  # The confidence over the course of the trees
        for condition, conditionEvalTree in zip(self._conditions, self._conditionTrees):
            # For each condition tree
            log.debug("Evaluating condition of the rule - {}".format(conditionEvalTree))
            confidence = conditionEvalTree.eval(scenario=scenario)/100  # Apply scenario
            
            scenarioConfidence += (1 - confidence)*(condition["salience"]/100)
            log.debug("Condition evaluated with confidence {}. Sum of error: {}".format(confidence, scenarioConfidence))
            
            if scenarioConfidence >= 1.0:
                log.debug("Evaluating scenarion ended - Conditions failed early returning 0")
                return 0

        scenarioConfidence = round((self.confidence/100)*(1 - scenarioConfidence)*100, 2)
        log.debug("Evaluated Scenario completed with confidence {}%".format(scenarioConfidence))
        return scenarioConfidence