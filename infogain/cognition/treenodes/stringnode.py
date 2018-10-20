from ..evaltrees import EvalTree

class StringNode(EvalTree):

    def __init__(self, string):
        self.string = string
    
    def __str__(self):
        return self.string

    def eval(self, **kwargs):
        return self.string