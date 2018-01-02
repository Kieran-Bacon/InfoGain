import re

#from .Ontology import Ontology
from .Concept import Concept
from .Condition import Condition

indentExpr = re.compile("^(\t| {4})")
statementExpr = re.compile("^%\w+ = .*$")

unboundExpr = re.compile("#(\[.+\]|)\w+(?!\w)")

unboundExpr = re.compile("#\[\w+\]\w+")
boundKeyExpr = re.compile("(?!\[)\w+(?=\])")

def extractUnbound(logic: str)->dict:

    variables = {}
    for pattern in unboundExpr.findall(logic):
        pass

        







class OntologyParser():

    indentExpr = re.compile("^(\t| {4})")

    def __init__(self, ontology):
        self.ontology = ontology

    def processWorldKnowledge(self, filepath = None, knowledge = None):
        print("Something")





            


class Statement():

    def __init__(self):
        self.something = None

