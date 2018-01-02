from itertools import product

from .Ontology import Ontology
from .Relation import Relation
from .Fact import Fact
from .Language import *

class ReasoningEngine( Ontology ):

    def __init__(self, name = None, filepath = None):
        super(ReasoningEngine, self).__init__(name, filepath)

        #self.transcientKnowledge = {"Concepts":[], "Facts":[]}
        self.relationEval = {}
        self.conditionEval = {}

    def addWorldKnowledge(self, filepath=None, knowledge=None):

        rawKnowledge = ""

        if filepath:
            with open( filepath, "r" ) as filehandler:
                rawKnowledge += filehandler.read()
        
        if knowledge:
            rawKnowledge += knowledge

        statements = [Statement(axiom) for axiom in Language.statementExpr.findall(rawKnowledge)]
        while statements:
            isApplied = False
            for i, statement in enumerate( statements ):
                execution = statement.execute(self)
                isApplied = execution
                if execution:
                    del statements[i]

            if not isApplied:
                raise ValueError( "Statements were not applied:" + "\n\t".join( statements ))            

        facts = []
        for axiom in rawKnowledge.split("\n"):

            if Language.statementExpr.search(axiom):
                continue

            if Language.indentExpr.search(axiom) is not None:
                axiom = axiom.strip()
                facts[-1].addCondition(Condition(axiom[:axiom.rfind(" ")], axiom[axiom.rfind(" ")+1:]))

            if Language.relationExpr.search(axiom) is not None:
                domain, relation, target, confidence = axiom.split(" ")
                domain = self.concept(domain)
                relation = self.relation(relation)
                target = self.concept(target)

                if relation.hasDomain(domain) and relation.hasTarget(target):
                    facts.append(Fact(domain, relation, target, confidence))
                else:
                    raise ValueError("World knowledge incorrect: " + axiom)

        [self.addFact(fact) for fact in facts]

    def evaluateRelation(self, relation: Relation) -> int:

        if relation in self.relationEval:
            return self.relationEval[relation]

        confidence = 0
        for fact in self._facts[relation.name]:
            confidence += (1-confidence)*self.evaluateFact(relation.domain, fact, relation.target)

        self.evaluateRelation[relation] = confidence


        pass

    def evaluateFact(self, fact: Fact) -> int:

        if fact in self.factEval:
            return self.factEval[fact] # Return the value of the fact.
        else:

            self.factEval[fact] = 0

            tags, concepts = [], []
            for tag, conceptName in fact.variables:
                tags.append(tag)
                concept = self.concept(conceptName)
                concepts.append([con for con in [concept] + concept.descendants() if not con.permable])

            scenrios = product( *concepts )
            for i, scene in enumerate(scenrios):
                scenrios[i] = {t:s for t,s in zip(tags, scene)}

            certainty = 0

            # Permutions of the fact conditions
            for scene in scenrios:

                salience = 100
                sceneCertainty = 0

                # Condition set of scene
                for condition in fact.apply(scene):

                    if condition["logic"] in self.conditionEval:
                        certainty += (self.conditionEval[condition["logic"]]/100)*(condition["salience"]/100)

                    value = (eval(condition["logic"])/100)*(condition["salience"]/100)

                    if value:
                        certainty += value
                        self.conditionEval[condition["logic"]] = value*100
                    else:
                        salience -= condition["salience"]

                certainty += sceneCertainty*(salience/100)



    def evaluateCondition(self, condition: Condition, scenrio) -> int:


                
        
        
        pass


    def evalRel(self, relation):

        

        for facts in self._facts[relation.name]:
            pass            