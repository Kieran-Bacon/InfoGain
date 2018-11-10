import re

from .decorators import scenario_consistent
from ..evaltrees import EvalTree

class OperatorNode(EvalTree):

    operators = {
        "==": lambda a, b : a == b,
        "!=": lambda a, b : a != b,

        ">(?!=)":  lambda a, b : a > b,
        "<(?!=)":  lambda a, b : a < b,
        ">=":  lambda a, b : a >= b,
        "<=":  lambda a, b : a <= b,

        r"\sis(?!\snot)\s":  lambda a, b : a is b,
        r"\sis\snot\s": lambda a, b : a is not b,
        r"\sand\s":  lambda a, b : a and b,
        r"\sor\s":  lambda a, b : a or b,
    }

    expression = re.compile(r".+(?P<operator>{}).+".format("|".join(operators.keys())))

    def __init__(self, left: EvalTree, operator: str, right: EvalTree):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self): return "{}{}{}".format(self.left, self.operator, self.right)
    def parameters(self): return self.left.parameters().union(self.right.parameters())

    def eval(self, **kwargs):
        return self.operators[self.operator](self.left.eval(**kwargs), self.right.eval(**kwargs))
