import itertools

from ..knowledge import Ontology, Concept, Instance, Rule, Condition
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
        *,
        supporting: bool = True,
        conditions: [Condition] = [],
        ontology: Ontology = None):

        Rule.__init__(self, domains, targets, confidence, supporting=supporting, conditions=conditions)

        self._conditionTrees = []
        self._parameters = {}
        self._evaluatedConfidences = {} 
        if ontology: self.assignOntology(ontology)

    def __repr__(self):
        super_repr = Rule.__repr__(self)
        return super_repr.replace("<Rule:", "<EvalRule:")

    def assignOntology(self, ontology: Ontology) -> None:
        """ Record a reference to the Ontology (InferenceEngine) that this EvalRule is a member of so that it may be
        able to generate Evaluable Trees for its logic, and to collect componets it needs during its evaluation
        
        Params:
            ontology (Ontology or InferenceEngine): The Ontology this object is a member of
        """
        
        # Record a reference to the engine
        self.engine = ontology

        # Generate a tree factory for against the engine
        self._factory = EvalTreeFactory(self.engine)

        # Generate the evaluable condition trees for the conditions objects
        self._conditionTrees = [self._factory.constructTree(cond.logic) for cond in self._conditions]

        # Find all the parameters within the logic and extract their concept definitions precisely
        self._parameters = {}
        for param in {param for tree in self._conditionTrees for param in tree.parameters()}.difference({"%", "@"}):
            self._parameters[param] = EvalTree.paramToConcept(param)

    def hasConditions(self, domain: Concept = None, target: Concept = None) -> bool:
        """ Check if the the rule has conditions, or, if the conditions apply, would they apply in 
        the instance that a domain and target pairing has been provided

        Params:
            domain (Concept): A concept or instance within the engine
            target (Concept): A concept or instance within the engine
        
        Returns:
            bool - True if no conditions or pairing has been evaluated else false
        """
        if domain is not None and target is not None and self:  # They have been provided
            if self._evaluatedConfidences.get(self._evalIdGen(domain, target)) is not None:  # There is a value for it
                return False
        
        return Rule.hasConditions(self)

    def eval(self, domain: Instance, target: Instance) -> float:
        """ Generate the confidence of the rule being true for the provided domain and target instance.

        Params:
            domain (Instance): The domain instance
            target (Instance): The target instance
        
        Returns:
            float: value between 0 - 100 that represents the confidence of the rule
        """

        if not self.applies(domain, target):
            log.debug("Rule doesn't apply to the paring, returning None")
            return 0  # Return 0 as the rule doesn't support the pair provided

        if not self._conditions:
            return self.confidence

        if not self._conditionTrees:
            raise RuntimeError("EvalRule({}) yet to construct condition trees - requires ontology/engine".format(self))

        pairing_key = self._evalIdGen(domain, target)  # Generate the key for this pairing

        if pairing_key in self._evaluatedConfidences:
            log.debug("Evaluating rule for {} {} - returning previous calculated value {}".format(
                domain, target, self._evaluatedConfidences[pairing_key]))
            return self._evaluatedConfidences[pairing_key]  # Returned previously evaluted score
        else:
            # Place an initial value to indicate that it is being evaluated
            self._evaluatedConfidences[pairing_key] = 0

        log.debug("Evaluating rule for {} {}".format(domain, target))

        # Collect together all the instances that may contribute to this rule, against the logic that represents them
        params = list(self._parameters.keys())
        instances = [self.engine.instances(*self._parameters[param]) for param in params]

        # Find the product of the instance sets 
        ruleConfidence = 1.0
        for scenario_instances in itertools.product(*instances):

            # Generate the scenario instances
            scenario = {param: scenario_instances[i] for i, param in enumerate(params)}
            scenario["%"] = domain
            scenario["@"] = target
            log.debug("Evaluating rule scenario - {}".format({k: str(v) for k,v in scenario.items()}))

            # Evaluate the scenario against all the conditions
            confidence = self.evalScenario(scenario)/100

            # TODO Fix this logic - I do not feel happy with the way in which we add up negitive outcomes.
            if confidence < -1 or confidence > 1: raise Exception("This is bad")
            if confidence < 0: confidence = 1 + confidence

            ruleConfidence *= (1.0-confidence)

        # Store the evaluation pairs outcome and return it
        pairing_key_confidence = (1.0 - ruleConfidence)*100
        self._evaluatedConfidences[pairing_key] = pairing_key_confidence
        return pairing_key_confidence

    def evalScenario(self, scenario: dict) -> float:
        """ Evaluate a particular scenario for the rule - given that the conditions contain unbound instance references,
        evaluate a particular scenario for the domain, target and the unbound instances

        Params:
            scenario (dict): A diction mapping the parameter representation in the logic to the instance to be inserted

        Returns:
            float: The confidence of the given scenario
        """

        scenarioConfidence = 0  # The confidence over the course of the trees
        for condition, conditionEvalTree in zip(self._conditions, self._conditionTrees):
            # For each condition tree
            log.debug("Evaluating condition of the rule - {}".format(conditionEvalTree))
            confidence = conditionEvalTree.eval(scenario=scenario)/100  # Apply scenario
            
            scenarioConfidence += (1 - confidence)*(condition.salience/100)
            log.debug("Condition evaluated with confidence {}. Sum of error: {}".format(confidence, scenarioConfidence))
            
            if scenarioConfidence >= 1.0:
                log.debug("Evaluating scenarion ended - Conditions failed early returning 0")
                return 0

        scenarioConfidence = round((self.confidence/100)*(1 - scenarioConfidence)*100, 2)
        log.debug("Evaluated Scenario completed with confidence {}%".format(scenarioConfidence))
        return scenarioConfidence

    def reset(self) -> None:
        """ Reset the EvalRule such that it doesn't persist its recorded confidences for domain target pairings that
        have been evaluated
        """
        self._evaluatedConfidences = {}

    @classmethod
    def fromRule(cls, rule: Rule, engine: Ontology):
        """ Convert a Rule onject from infogain.knowledge into an EvalRule object
        
        Params:
            rule (knowledge.Rule): The rule to be converted
            engine (Ontology): The ontology to be assigned to the newly generated EvalRule
        """
        return EvalRule(
            rule.domains,
            rule.targets,
            rule.confidence,
            supporting=rule.supporting,
            conditions=rule.conditions(),
            ontology=engine
        )

    @staticmethod
    def _evalIdGen(domain: Concept, target: Concept) -> str:
        """ Generate an id for a evaluation pairing

        Params:
            domain (Concept, Instance): The domain that was used during evaluation
            target (Concept, Instance): The target that was used during evaluation
        """
        return "-".join([domain.name, target.name])