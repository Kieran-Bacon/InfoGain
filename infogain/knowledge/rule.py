from .concept import Concept

class Rule:
    """ A rule is used to express how a relation might come about given a collection of knowledge """

    def __init__(self, domains: {Concept}, relation: str, targets: {Concept}, confidence: float, conditions: [dict] = []):

        if isinstance(domains, (Concept, str)):
            domains = {domains}
            targets = {targets}

        self.domains = set(domains)
        self.relation = relation
        self.targets = set(targets)

        self.confidence = confidence
        self._conditions = sorted(conditions, key = lambda x: x["salience"])

        variableOnTarget = False
        for condition in conditions:
            if "@" in condition["logic"]:
                variableOnTarget = True
                break

        if conditions:
            self.domains = Concept.expandConceptSet(self.domains)
            self.targets = Concept.expandConceptSet(self.targets, descending=False)

            if variableOnTarget:
                self.targets = self.targets.union(Concept.expandConceptSet(targets))

    def applies(self, domain: (Concept), target: (Concept)):
        """ Determine if the rule applies to the the domain and target pairing that has been
        provided """
        if Concept.ABSTRACT == (domain.category or target.category): return False
        else: return domain in self.domains and target in self.targets

    def minimise(self):
        """ Reduce the rule down to a dictionary object of definitions """

        domains = sorted([con.name if isinstance(con, Concept) else con for con in Concept.minimiseConceptSet(self.domains)])
        targets = sorted([con.name if isinstance(con, Concept) else con for con in Concept.minimiseConceptSet(self.targets, ascending=False)])
        relation = self.relation

        minimised = {"domains": domains, "relation": relation, "targets": targets, "confidence": self.confidence }

        if self._conditions:
            minimised["conditions"] = self._conditions

        return minimised

    def clone(self):
        return Rule(**self.minimise())