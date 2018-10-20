import re

from ..evaltrees import EvalTree

class NumberNode(EvalTree):

    expression = re.compile(r"(^\d+\.\d+$|^\d+$)")

    def __init__(self, number):
        self.number = float(number)

    def __str__(self):
        if int(self.number) == self.number: return str(int(self.number))
        return str(self.number)

    def eval(self, **kwargs):
        return self.number