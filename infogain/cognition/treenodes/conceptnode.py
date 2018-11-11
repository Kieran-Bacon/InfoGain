import re

from ...knowledge import Instance

from ..evaltrees import EvalTree
from ...exceptions import ConsistencyError, IncorrectLogic

from .decorators import *

class ConceptNode(EvalTree):

    expression = re.compile(r"(^\s*){}(\s*$)".format(EvalTree.concept_syntax.pattern))
    
    def __init__(self, concept_name: str, callparameters: [object] = None):
        self.concept_name = concept_name
        self.callparameters = callparameters

        self.__scenario_requires__ = [self.concept_name]

    def __str__(self):

        string = self.concept_name
        if self.callparameters is not None:
            string = "{}({})".format(string, ",".join([str(param) for param in self.callparameters]))

        return string

    @scenario_consistent
    def instance(self, **kwargs):

        instance = kwargs["scenario"][self.concept_name]

        if self.callparameters:
            instance = instance(*self._evaluatedParameters(**kwargs))
            if not isinstance(instance, Instance) and kwargs.get("ignore") != True:
                raise RuntimeError("Concept Node {} does not yeild an instance.".format(self))

        return instance

    @scenario_consistent
    def eval(self, **kwargs):

        if self.callparameters is not None: return self.instance(**kwargs, ignore=True)
        else: return 100

    def _evaluatedParameters(self, **kwargs):
        """ Evaluate all the parameters in the call parameters and return a list of their results """
        return [param.eval(**kwargs) for param in self.callparameters]

    def parameters(self):
        return {self.concept_name}