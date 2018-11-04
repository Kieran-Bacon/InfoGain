import re

from .conceptnode import ConceptNode
from .decorators import scenario_consistent
from ..evaltrees import EvalTree

class PropertyNode(EvalTree):

    expression = re.compile(r"(?P<flection_point>\.)(?P<property_name>[A-Za-z][\w_]*)(?!.*\.)")

    def __init__(self, component: str, property_key: str, parameters: [EvalTree] = None):
        self.component = component
        self.property_key = property_key
        self.function_parameters = parameters

    def __str__(self):
        string = "{}.{}".format(self.component, self.property_key)
        if self.function_parameters is not None: string += "({})".format(",".join([str(param) for param in self.function_parameters]))
        return string

    def parameters(self):
        return self.component.parameters()

    @scenario_consistent
    def instance(self, **kwargs): return self.component.instance(**kwargs)

    @scenario_consistent
    def eval(self, **kwargs):
        """ Extract the property from the object on the left """

        instance = self.component.instance(**kwargs)

        if self.function_parameters is not None:
            print("Got here")
            return instance.__getattribute__(self.property_key)(*[param.eval(**kwargs) for param in self.function_parameters])
        else:
            return instance[self.property_key]