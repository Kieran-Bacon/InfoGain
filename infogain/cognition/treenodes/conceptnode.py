import re

from ..evaltrees import EvalTree
from ...exceptions import ConsistencyError

class ConceptNode(EvalTree):

    systax = re.compile(r"\%|\@|#[\w_]+")
    expression = re.compile(r"(^\s*)({})(\s*$)".format(systax.pattern))
    
    def __init__(self, concept_name: str):
        self.concept_name = concept_name

    def __str__(self):
        return self.concept_name

    def instance(self, **kwargs):
        if "scenario" not in kwargs: raise ConsistencyError("A valid scenario has not been passed through evaluation stack")
        if kwargs["scenario"].get(self.concept_name) is None: raise ConsistencyError("Logic error - Concept node for {} not found in scenario".format(self.concept_name))
        return kwargs["scenario"].get(self.concept_name)

    def eval(self, **kwargs):
        if "scenario" in kwargs: return (kwargs["scenario"].get(self.concept_name) is not None)*100
        else: return 0

    def parameters(self):
        return {self.concept_name}