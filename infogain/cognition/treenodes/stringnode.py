from ..evaltrees import EvalTree

class StringNode(EvalTree):

    def __init__(self, string: str):

        a = string.strip()
        if a[0] in ["'", '"'] and a[0] == a[-1]: string = a[1:-1]  
        self.string = string
    
    def __str__(self):
        return self.string

    def eval(self, **kwargs):
        return self.string