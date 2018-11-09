import re

from .conceptnode import ConceptNode
from .decorators import scenario_consistent
from ..evaltrees import EvalTree

class PropertyNode(EvalTree):
    """ A property nodes handles the extraction of information from the concepts, relations or node evaluation outcomes.
    It implements the extraction of information indistingishably from that of python.

    It is additionally responsible for calling object functions.

    #example.prop.to.be.extracted

    Params:
        component (EvalTree): The tree node handling the object we are to collect the property from
        property_key (str): The property key string
        parameters ([EvalTree]): If provided, the property is called with these parameters
    """

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
            return instance.__getattribute__(self.property_key)(*[param.eval(**kwargs) for param in self.function_parameters])
        else:
            return instance[self.property_key]