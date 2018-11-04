import re

from ..exceptions import IncorrectLogic, ConsistencyError
from ..knowledge import Instance

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

from .treenodes import *

class EvalTreeFactory:
    """ Evaluable logic tree factory - Converts a logical string into a complex tree structure
    that may be evaluated. Tree's can be comprised of EvalNodes that all inherit from EvalTree. Each
    Node descripts how the language of the logic is used.
    
    Params:
        engine (InferenceEngine): Reference to the inference engine - the scope of the logic
    """

    def __init__(self, engine):
        self._depth = 0
        self.engine = engine

    def constructTree(self, logic) -> EvalTree:
        """ Wrapper function for private node generator - ensures recursively generated nodes
        have the information they need to function 
        
        #TODO: Documentation"""

        self._depth += 1
        node = self._constructTree(logic)
        self._depth -= 1

        if not self._depth and isinstance(node, StringNode):
            raise IncorrectLogic("The logic provided shall only ever yield a string - {}".format(logic))
            # Top of recursion
        node._assignEngine(self.engine)
        return node

    def _constructTree(self, logic):
        if not logic: raise IncorrectLogic("Empty logic - cannot construct tree for literally nothing...")

        # Break down the logic into its top level information and its various sections
        tll, segments = self._breakdown_logic(logic)

        # The Logic was surrounded by parenthesis - Remove them and call again
        if not tll and len(segments) == 1: return self.constructTree(segments[0][1][1:-1])

        try:
            match = PropertyNode.expression.search(tll)
            if match:

                # Split by the inflection point, 
                left, _ = self._reformSplit(tll, segments, match.span("flection_point"))

                parameters = None
                for segment in segments:
                    if segment[0] == match.span()[1]:
                        parameters = self._buildParameters(segment[1])
                        break

                return PropertyNode(self.constructTree(left), match.group("property_name"), parameters)

            match = RelationNode.expression.search(tll)
            if match:
                domain, relation, target, isPositive = RelationNode.split(tll)
                return RelationNode(self.constructTree(domain), relation, self.constructTree(target), isPositive)

            match = ConceptNode.expression.search(tll)
            if match:
                # Construct a concept node
                if 0 > len(segments) > 1: raise IncorrectLogic("Weird amount of segments provided to this...") # TODO improve raise message
                parameters = self._buildParameters(segments[0][1]) if len(segments) else None
                return ConceptNode(match.group(0), callparameters=parameters)

            if tll in BuiltInFunctionNode.functionList:
                if len(segments) != 1: raise IncorrectLogic()  # TODO look into this and why its the way that it is.
                return BuiltInFunctionNode(tll, self._buildParameters(segments[0][1]))
            
            match = NumberNode.expression.search(tll)
            if match: return NumberNode(match.group(2))

            return StringNode(logic)
        except IncorrectLogic as e:
            raise IncorrectLogic("Could not parse sub logic for {}".format(logic)) from e

    def _buildParameters(self, logic: str): # TODO Document
        """ Build the parameters from a logic string and return the collection of EvalTrees 
        constructed """
        logic = logic.strip("()")
        logic = logic.split(",")
        if logic == [""]: return []
        else: return [self.constructTree(param) for param in logic]

    @staticmethod
    def paramToConcept(concept_name: str) -> str:  # TODO FIX THIS FUNCTION
        """ Convert a parameter name into a valid concept string 
        
        # TODO: Documentation"""
        match = re.search("[A-Za-z_]+", concept_name)
        if match: return match.group(0), "#" in concept_name

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