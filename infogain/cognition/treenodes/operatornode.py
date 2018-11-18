import re

from .decorators import scenario_consistent
from ..evaltrees import EvalTree

from collections import namedtuple
Operator = namedtuple("Operator", ["expression", "function"])

class OperatorNode(EvalTree):

    operators = {
        "+":        Operator(r"\+", lambda a, b : a + b),
        "-":        Operator(r"\s+-\s+", lambda a, b : a - b),
        "*":        Operator(r"\*(?!\s*\*)", lambda a, b : a * b),
        "**":       Operator(r"\*\s*\*", lambda a, b : a ** b),
        "/":        Operator(r"/(?!/)", lambda a, b : a / b),
        "//":       Operator(r"//", lambda a, b : a // b),
        "%":        Operator(r"\s%\s", lambda a, b : a % b),

        "==":       Operator(r"==", lambda a, b : a == b),
        "!=":       Operator(r"!=", lambda a, b : a != b),

        ">":        Operator(r">(?!=)", lambda a, b : a > b),
        "<":        Operator(r"<(?!=)", lambda a, b : a < b),
        ">=":       Operator(r">=", lambda a, b : a >= b),
        "<=":       Operator(r"<=", lambda a, b : a <= b),

        " is ":     Operator(r"\sis(?!\snot)\s", lambda a, b : a is b),
        " is not ": Operator(r"\sis\snot\s", lambda a, b : a is not b),
        " and ":    Operator(r"\sand\s", lambda a, b : a and b),
        " or ":     Operator(r"\sor\s", lambda a, b : a or b),
    }

    expression = re.compile(r".+(?P<operator>{}).+".format("|".join([op.expression for op in operators.values()])))

    def __init__(self, left: EvalTree, operator: str, right: EvalTree):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self): return "{}{}{}".format(self.left, self.operator, self.right)
    def parameters(self): return self.left.parameters().union(self.right.parameters())

    def eval(self, **kwargs):
        return self.operators[self.operator].function(self.left.eval(**kwargs), self.right.eval(**kwargs))
