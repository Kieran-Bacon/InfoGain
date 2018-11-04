import re

from ..evaltrees import EvalTree
from .decorators import scenario_consistent

class FunctionNode(EvalTree):

    expression = re.compile(r">")

    def __init__(self, component: EvalTree, function_name: str, parameters: [EvalTree]):
        self.component = component
        self.function = function_name
        self.function_parameters = parameters

    def __str__(self):
        return str(self.component) + ">" + str(self.function) + "({})".format(",".join([str(x) for x in self.function_parameters]))

    def parameters(self):
        return self.component.parameters().union({param for group in self.function_parameters for param in group.parameters()})

    @scenario_consistent
    def eval(self, **kwargs):

        function = self.component.instance(**kwargs).__getattribute__(self.function)
        return function(*[param.eval(**kwargs) for param in self.function_parameters]) if function else None 