import re

from .decorators import scenario_consistent
from ..evaltrees import EvalTree

def equal(a, b): return a == b
def notEqual(a, b): return a != b

class OperatorNode(EvalTree):

    operators = {
        "==": equal,
        "!=": notEqual
    }

    expression = re.compile(r".+(?P<operator>{}).+".format("|".join(operators)))

    def __init__(self, left: EvalTree, operator: str, right: EvalTree):
        self.left = left
        self.operator = operator
        self.right = right

    @scenario_consistent
    def eval(self, **kwargs):
        return self.operators[self.operator](self.left.eval(**kwargs), self.right.eval(**kwargs))
