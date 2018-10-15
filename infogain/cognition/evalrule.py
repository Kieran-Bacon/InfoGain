import itertools

from ..knowledge import Ontology, Concept, Instance, Rule
from .evaltrees import EvalTreeFactory, EvalTree

import logging
log = logging.getLogger(__name__)

class EvalRule(Rule):
    """ As part of a inference engine, an EvalRule is able to use evaluate its internal logic and 
    return with a confidence for a domain target paring that has been passed. The object is 
    responsible for generating all relevant scenarios and combining their confidences

    Params:
        domains ({Concept}): A subset of the relation domains that this rule applies too
        targets ({Concept}): A subset of the relation targets that this rul applies too
        confidence (float): The maximum certainty this rule can generate
        supporting (bool): Indicates whether this rule agrees with a relation or undermines it -
                           if True confidence goes up else confidence goes down
        conditions ([dict]): A list of dictionaries containing the definition for logical conditions
                            that would need to be meet for the rule to be valid
        ontology (Ontology): The inference engine refer needed for the evaluation of some logic
    """

    def __init__(self,
        domains: {Concept},
        targets: {Concept},
        confidence: float,
        supporting: bool = True,
        conditions: [dict] = [],
        ontology: Ontology = None):

        Rule.__init__(self, domains, targets, confidence, conditions)

        self.supporting = supporting
        self._evaluatedConfidences = {} 
        if ontology: self.assignOntology(ontology)

    def assignOntology(self, ontology: Ontology) -> None:
        """ Assign the ontology object to the rule and link the correct variables """
        self.engine = ontology

        self.domains = {self.engine.concept(con) for con in self.domains if isinstance(con, str)}.union(self.domains)
        self.targets = {self.engine.concept(con) for con in self.targets if isinstance(con, str)}.union(self.targets)

        self._factory = EvalTreeFactory(self.engine)
        self._conditionTrees = [self._factory.constructTree(cond["logic"]) for cond in self._conditions]

        self._parameters = {}
        for tree in self._conditionTrees:
            for param in tree.parameters():
                self._parameters[param] = EvalTreeFactory.paramToConcept(param)


        self._parameters = {param for tree in self._conditionTrees for param in tree.parameters()}.difference({"%", "@"})

    def eval(self, domain: Instance, target: Instance):
        """ Evaluate all the scenarios of a particular relation instance and determine the confidence
        of the relation """

        if domain.concept not in self.domains and target.concept not in self.targets:
            log.debug("Rule doesn't apply to the paring, returning None")
            return 0  # Return 0 as the rule doesn't support the pair provided

        if not self._conditions:
            return self.confidence

        pairing_key = "-".join([str(domain), str(target)])  # Generate the key for this pairing

        if pairing_key in self._evaluatedConfidences:
            log.debug("Evaluating rule for {} {} - returning previous calculated value {}".format(domain, target, self._evaluatedConfidences[pairing_key]))
            return self._evaluatedConfidences[pairing_key]  # Returned previously evaluted score

        log.debug("Evaluating rule for {} {}".format(domain, target))

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

            log.debug("Evaluating rule scenario - {}".format({k: str(v) for k,v in scenario.items()}))

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