import re

from ..exceptions import IncorrectLogic, ConsistencyError
from ..knowledge import Instance

import logging
log = logging.getLogger(__name__)

class EvalTree:
    
    def __str__(self):
        raise NotImplementedError()

    def _assignEngine(self, engine):
        self.engine = engine
    
    def instance(self, *args) -> Instance:
        """ return the instance this node is linked too or None in the event the node does not
        relate """
        return None

    def parameters(self) -> set:
        """ Determine the parameters that are contained within the node """
        return set()

    def eval(self, *args, **kwargs):
        """ Determine the value of the node and return its value """
        raise NotImplementedError()

class ConceptNode(EvalTree):

    expression = re.compile(r"\%|\@|#[\w_]+")
    
    def __init__(self, concept_name: str):
        self.concept_name = concept_name

    def __str__(self):
        return self.concept_name

    def instance(self, **kwargs):
        if "scenario" not in kwargs: raise ConsistencyError("A valid scenario has not been passed through evaluation stack")
        if kwargs["scenario"].get(self.concept_name) is None: raise ConsistencyError("Logic error - Concept node for {} not found in scenario".format(self.concept_name))
        return kwargs["scenario"].get(self.concept_name)

    def eval(self, **kwargs):
        if "scenario" in kwargs: return (kwargs["scenario"].get(self.concept_name) is not None)*100
        else: return 0

    def parameters(self):
        return {self.concept_name}

class RelationNode(EvalTree):

    # TODO: Handle negative relations
    expression = re.compile(r"({})=([\w_]+)=({})".format(ConceptNode.expression.pattern, ConceptNode.expression.pattern))
    
    def __init__(self, domain: ConceptNode, relation: str, target: ConceptNode):
        self.domain = domain
        self.relation = relation
        self.target = target

    def __str__(self):
        return "=".join([str(self.domain), self.relation, str(self.target)])

    def parameters(self):
        return self.domain.parameters().union(self.target.parameters())

    def eval(self, **kwargs):
        return self.engine.inferRelation(self.domain.instance(**kwargs), self.relation, self.target.instance(**kwargs))

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

class FunctionNode(EvalTree):

    expression = re.compile(r">")

    def __init__(self, component: Instance, function_name: str, parameters: [EvalTree]):
        self.component = component
        self.function = function_name
        self.function_parameters = parameters

    def __str__(self):
        return str(self.component) + ">" + str(self.function) + "({})".format(",".join([str(x) for x in self.function_parameters]))

    def parameters(self):
        return self.component.parameters().union({param for group in self.function_parameters for param in group.parameters()})

    def eval(self, **kwargs):

        function = self.component.instance(**kwargs).__getattribute__(self.function)
        return function(*[param.eval(**kwargs) for param in self.function_parameters]) if function else None 

class BuiltInFunctionNode(EvalTree):

    functionList = [
        "graph"
    ]

    def __init__(self, function_name: str, parameters: [EvalTree]):

        self.__function_list = {
            "graph": self.graph
        }

        log.info("Created BuildInFunctionNode {}".format(function_name))
        self.function = function_name
        self.function_parameters = parameters

    def __str__(self):
        return self.function + "({})".format(",".join(self.function_parameters))

    def parameters(self):
        return [param for func_param in self.function_parameters for param in func_param.parameters()]

    def eval(self, **kwargs):

        function_parameters = [node.eval(**kwargs) for node in self.function_parameters]

        return self.__function_list[self.function](*function_parameters)

    @staticmethod
    def graph(*args):

        assert(len(args) > 0)

        expression = args[-1].replace("'", "").replace('"', "")
        
        function_list = []
        for char in expression:
            function_list.append(char)
            if re.search("[A-Za-z]", char): function_list.append(" ")
        function_string = "".join(function_list)

        parameters = [float(param) for param in args[:-1]]
        variables = []
        for var in re.findall(r"[A-Za-z]", function_string):
            if var not in variables: variables.append(var)

        assert(len(parameters) ==  len(variables))

        return eval(function_string, {var: par for var, par in zip(variables, parameters)})

class StringNode(EvalTree):

    def __init__(self, string):
        self.string = string
    
    def __str__(self):
        return self.string

    def eval(self, **kwargs):
        return self.string

class NumberNode(EvalTree):

    expression = re.compile(r"(^\d+\.\d+$|^\d+$)")

    def __init__(self, number):
        self.number = float(number)

    def __str__(self):
        if int(self.number) == self.number: return str(int(self.number))
        return str(self.number)

    def eval(self, **kwargs):
        return self.number

class EvalTreeFactory:

    def __init__(self, engine):
        self.engine = engine

    def constructTree(self, logic) -> EvalTree:
        """ Wrapper function for private node generator - ensures recursively generated nodes
        have the information they need to function """
        node = self.__constructTree(logic)
        node._assignEngine(self.engine)
        return node

    def __constructTree(self, logic):

        if not logic: raise IncorrectLogic("Empty logic")
        tll, segments = self._breakdown_logic(logic)

        if not tll and len(segments) == 1:
            # Remove all encompassing parenthesis
            return self.constructTree(segments[0][1][1:-1])

        # The logic contains a concept function as the main pivort
        match = FunctionNode.expression.search(tll)
        if match:
            left, right = self._reformSplit(tll, segments, match.span())
            function, signature = right[:right.index("(")], right[right.index("("):][1:-1].split(",")
            parameters = [self.constructTree(sigParam) for sigParam in signature if sigParam != ""]
            return FunctionNode(self.constructTree(left), function, parameters)

        # Property key of component is main pivort
        match = PropertyNode.expression.search(tll)
        if match:
            left, right = self._reformSplit(tll, segments, match.span())
            return PropertyNode(self.constructTree(left), right)

        match = RelationNode.expression.search(tll)
        if match:
            domain, relation, target = tll.split("=")
            return RelationNode(self.constructTree(domain), relation, self.constructTree(target))

        match = ConceptNode.expression.search(tll)
        if match:
            return ConceptNode(tll)

        if tll in BuiltInFunctionNode.functionList:
            if len(segments) != 1: raise IncorrectLogic()
            parameters = [self.constructTree(param) for param in segments[0][1][1:-1].split(",")]
            return BuiltInFunctionNode(tll, parameters)
        
        match = NumberNode.expression.search(tll)
        if match:
            return NumberNode(tll)

        return StringNode(tll)

    @staticmethod
    def _breakdown_logic(logic: str) -> (str, (int, str)):
        """ Break down the logic provided into top level logic, along with accompanying secondary
        logic captures.
        """

        # The currently openned parenthesis index + the number of inner open parenthesis before its close
        indexOfOpenned, ignoreCount = None, 0  
        segments = []

        for i, char in enumerate(logic):
            if char is "(":
                if indexOfOpenned is None: indexOfOpenned = i  # Found a new segment, record index
                else: ignoreCount += 1  # Found open parethesis between open and close

            if char is ")":
                if indexOfOpenned is None: raise IncorrectLogic("Parenthesis miss match")

                if ignoreCount: ignoreCount -= 1  # Closed a inbetween segment
                else:
                    # Segment complete, record segment and remove reference to open parenthesis
                    segments.append((indexOfOpenned, i))
                    indexOfOpenned = None

        if indexOfOpenned: raise IncorrectLogic("Parenthesis miss match")

        # Split the logic now via the segments

        # The top level logic string + the number of removed characters for index updating
        top_level_logic, removedCounter = logic, 0
        tllSegmentsMap = []  # Record of index of the top level string where segments are to be inserted

        for i, j in segments:
            correctedi, correctedj = i-removedCounter, (j+1)-removedCounter
            tllSegmentsMap.append((correctedi, logic[i:j+1]))  # Record the segment
            top_level_logic = top_level_logic[:correctedi] + top_level_logic[correctedj:]  # Remove segment
            removedCounter += (j+1) - i  # Update removed character count

        return top_level_logic, tllSegmentsMap

    @staticmethod
    def _reformSplit(logic: str, segments: (int, str), split_span: (int, int)) -> (str, str):
        """ Expand the logic with the provided removed segments, and split the newly regenerated 
        logic string via the split span of the originally provided logic
        """

        # Seperate logic and segments
        left, right = logic[:split_span[0]], logic[split_span[1]:]
        leftSegs, rightSegs = [], []

        for index, segStr in segments:
            if index <= split_span[0]: leftSegs.append((index, segStr))
            else: rightSegs.append((index - len(logic[:split_span[1]]), segStr))  # Correct index

        def addSegments(minLogic, segments):
            expandedLogic, addedCount = minLogic, 0

            for i, segment in segments:
                correctedi = i + addedCount
                expandedLogic = expandedLogic[:correctedi] + segment + expandedLogic[correctedi:]
                addedCount += len(segment)

            return expandedLogic

        # Construct left and right and return
        return addSegments(left, leftSegs), addSegments(right, rightSegs)

    @staticmethod
    def paramToConcept(concept_name: str) -> str:
        """ Convert a parameter name into a valid concept string """
        match = re.search("[A-Za-z_]+", concept_name)
        if match: return match.group(0), "#" in concept_name