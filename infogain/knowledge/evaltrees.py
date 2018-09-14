import logging, re

log = logging.getLogger(__name__)

class IncorrectLogic(Exception):
    pass

class EvalTreeNode:
    
    def __str__(self):
        raise NotImplementedError()

    def eval(self, *args):
        raise NotImplementedError()

class PipeNode(EvalTreeNode):

    def __init__(self, left, right):
        log.info("Created PipeNode")

        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + "->" + str(self.right)

class PropertyNode(EvalTreeNode):

    def __init__(self, component: str, property_key: str):
        self.component = component
        self.key = property_key

    def __str__(self):
        return str(self.component) + "." + str(self.key)

class ConceptNode(EvalTreeNode):
    
    def __init__(self, concept_name: str):
        self.concept = concept_name

    def __str__(self):
        return self.concept

class ConceptFunctionNode(EvalTreeNode):

    def __init__(self, concept: ConceptNode, function_name: str, parameters: [EvalTreeNode]):
        self.concept = concept
        self.function = function_name
        self.parameters = parameters

    def __str__(self):
        return str(self.concept) + ">" + str(self.function) + "({})".format(",".join([str(x) for x in self.parameters]))

class RelationNode(EvalTreeNode):
    
    def __init__(self, domain: ConceptNode, relation: str, target: ConceptNode):
        self.domain = domain
        self.relation = relation
        self.target = target

class BuiltInFunctionNode(EvalTreeNode):

    def __init__(self, function_name: str, parameters: str):
        log.info("Created BuildInFunctionNode {}".format(function_name))
        self.function = function_name
        self.parameters = parameters[1:-1].split(",")

    def __str__(self):
        return self.function + "({})".format(",".join(self.parameters))

class EvalTreeFactory:

    __PipeFunction = re.compile(r"->")
    __ConceptFunction = re.compile(r">")
    __Property = re.compile(r"\.")

    __Concept = re.compile(r"\%|\@|#[\w_]+")
    __Relation = re.compile(r"({})=([\w_]+)=({})".format(__Concept.pattern, __Concept.pattern))

    __String = re.compile(r"\".+\"")
    __Number = re.compile(r"(\d+\.\d+|\d+)")

    __buildinFunction = {"map", "min", "multiply"}

    def __init__(self, ontology):

        self.ontology = ontology

    def constructTree(self, logic) -> EvalTreeNode:

        if not logic: raise IncorrectLogic("Empty logic")
        tll, segments = self._breakdown_logic(logic)

        if not tll and len(segments) == 1:
            # Remove all encompassing parenthesis
            return self.constructTree(segments[0][1][1:-1])

        # The logic contains a piping function
        match = self.__PipeFunction.search(tll)
        if match:
            # Reform the logic on the split
            left, right = self._reformSplit(tll, segments, match.span())
            return PipeNode(self.constructTree(left), self.constructTree(right))

        # The logic contains a concept function as the main pivort
        match = self.__ConceptFunction.search(tll)
        if match:
            if len(segments) != 1: raise IncorrectLogic()
            left, right = self._reformSplit(tll, segments, match.span())

            function, signature = right[:right.index("(")], right[right.index("("):][1:-1].split(",")

            parameters = [self.constructTree(sigParam) for sigParam in signature]

            return ConceptFunctionNode(self.constructTree(left), function, parameters)

        # Property key of component is main pivort
        match = self.__Property.search(tll)
        if match:
            left, right = self._reformSplit(tll, segments, match.span())
            return PropertyNode(self.constructTree(left), right)

        match = self.__Relation.search(tll)
        if match:
            domain, relation, target = tll.split("=")
            return RelationNode(self.constructTree(domain), relation, self.constructTree(target))

        match = self.__Concept.search(tll)
        if match:
            return ConceptNode(tll)

        match = self.__String.search(tll)
        if match:
            return re.escape(tll)
        
        match = self.__Number.search(tll)
        if match:
            return float(tll)

        if tll in self.__buildinFunction:
            if len(segments) != 1: raise IncorrectLogic()
            return BuiltInFunctionNode(tll, segments[0][1])

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



class EvalTreeleaf:
    pass

if __name__ == "__main__":

    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    logic = "map(3, x**2)->min(4)->multiply(%=rel1=@)->map(x>2)"

    TreeFactory = EvalTreeFactory(None)

    node = TreeFactory.constructTree(logic)
    log.info(node)

    log.info(TreeFactory.constructTree("#Time>length(%.start_date, @.start_date)->map(x>0)"))
    log.info(TreeFactory.constructTree("(#Time>length(%.start_date, @.start_date))->(map(x>0))"))