import re

from ..evaltrees import EvalTree
from ...exceptions import ConsistencyError

class ConceptNode(EvalTree):

    systax = re.compile(r"\%|\@|#(\[[\w_]+\])?[\w_]+")
    expression = re.compile(r"(^\s*)({})(\s*$)".format(systax.pattern))
    
    def __init__(self, concept_name: str, callparameters: [object] = None):
        self.concept_name = concept_name
        self.callparameters = callparameters

    def __str__(self):

        string = self.concept_name
        if self.callparameters is not None:
            string = "{}({})".format(string, ",".join([str(param) for param in self.callparameters]))

        return string

    def instance(self, **kwargs):
        if "scenario" not in kwargs: raise ConsistencyError("A valid scenario has not been passed through evaluation stack")
        if kwargs["scenario"].get(self.concept_name) is None: raise ConsistencyError("Logic error - Concept node for {} not found in scenario".format(self.concept_name))
        return kwargs["scenario"].get(self.concept_name)

    def eval(self, **kwargs):

        if self.callparameters is not None:
            # The node is to use its instance's call function
            instance = self.instance(**kwargs)
            if instance is None: raise ConsistencyError("A valid scenario has not been passed through evaluation stack")  # TODO improve message
            return instance(*[param.eval(**kwargs) for param in self.callparameters])

        if "scenario" in kwargs: return (self.instance(**kwargs) is not None)*100
        else: return 0

    def parameters(self):
        return {self.concept_name}