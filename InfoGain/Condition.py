import re

class Condition:

    unboundExpr = re.compile("#\[\w+\]\w+")
    boundKeyExpr = re.compile("(?!\[)\w+(?=\])")

    def __init__(self, logic, salience):

        self.logic = logic
        self.salience = salience
        self.parameters = {}

        for unboundParameter in unboundExpr.findall(self.logic):

            key = unboundParameter[unboundParameter.index("[")+1:unboundParameter.index("]")]
            concept = unboundParameter[unboundParameter.index("]")+1:]

            if key in self.parameters:
                raise ValueError("Logic contains multiple parameters with the same key")

            self.parameters[key] = concept

    def parameters(self):
        return self.parameters
    
    def instance(self, domain: str, target: str, parameterSet: dict):
        """ Return an instance for the parameter set provided """

        # Replace domain and target
        intLogic = re.sub("$", "#" + domain.name, self.logic)
        intLogic = re.sub("@", "#" +target.name, intLogic)

        for key, concept in parameterSet.items():
            intLogic = re.sub("#\[\\" + key + "\]\w+", "#"+concept, intLogic)

        return ConditionInstance(intLogic)


class ConditionInstance:
    """ A condition that has a set domain, target and unbound parameters """

    def __init__(self, logic):
        self.logic = logic
        self.confidence = None

    def __eq__(self, other):
        return self.logic == other.logic

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.logic)