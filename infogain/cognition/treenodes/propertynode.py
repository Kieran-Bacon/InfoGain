import re

from ..evaltrees import EvalTree

class PropertyNode(EvalTree):

    expression = re.compile(r"(?!([0-9]*[A-Za-z]+[0-9]*)+)\.(?=([0-9]*[A-Za-z]+[0-9]*)+)")

    def __init__(self, component: str, property_key: str):
        self.component = component
        self.key = property_key

    def __str__(self):
        return str(self.component) + "." + str(self.key)

    def parameters(self):
        return self.component.parameters()

    def eval(self, **kwargs):
        """ Extract the property from the object on the left """
        return self.component.instance(**kwargs)[self.key]