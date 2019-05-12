import re

from ..exceptions import IncorrectLogic, ConsistencyError
from ..knowledge import Instance

class EvalTree:

    concept_syntax = re.compile(r"\%|\@|#(\[[\w_]+\])?([A-Za-z][\w_]*)")  # The concept syntax in the logic
    
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

    @classmethod
    def isPlaceholder(cls, concept_name: str):
        """ Identify whether the provided concept_name is actually just a valid placeholder for a concept, the concept
        name itself doesn't contain the information to determine its own concept.

        Params:
            concept_name (str): The potential concept name to be tested
        """
        return concept_name in ["%", "@"] 

    @classmethod
    def paramToConcept(cls, concept_name: str) -> (str, bool):
        """ Convert a parameter name into a valid concept string 

        Params:
            concept_name (str): String that expresses a concept

        Returns:
            str: A valid concept name
            bool: Identifies that the concept is meant to be expanded to include its children.
        """
        match = cls.concept_syntax.search(concept_name)
        if match and match.group(2): return match.group(2), "#" in match.group(0)
        else: raise ValueError("Could not match concept definition with provided string: {}".format(concept_name))

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
        """ Convert the provided logic into a EvalTree structure. The Eval tree is the root node of a tree who's
        complexity is dependant on the logic.

        Params:
            logic (str): The logic to be parsed
        
        Returns:
            EvalTree: Root of a complex tree structure

        Raises:
            IncorrectLogic: When the logic is poorly writen and a syntax error has occured
        """

        self._depth += 1
        node = self._constructTree(logic)
        self._depth -= 1

        if not self._depth and isinstance(node, StringNode): # Check run only for top of tree recursion
            raise IncorrectLogic("The logic provided shall only ever yield a string - {}".format(logic))

        # Pass reference to the engine to each of the nodes within the tree   
        node._assignEngine(self.engine)
        return node

    def _constructTree(self, logic):
        if not logic: raise IncorrectLogic("Empty logic - cannot construct tree for literally nothing...")

        # Break down the logic into its top level information and its various sections
        tll, segments = self._breakdown_logic(logic)

        # The Logic was surrounded by parenthesis - Remove them and call again
        if not tll or tll.isspace() and len(segments) == 1: return self.constructTree(segments[0][1][1:-1])

        try:
            match = StringNode.expression.search(logic)
            if match: return StringNode(logic)

            match = NumberNode.expression.search(tll)
            if match: return NumberNode(match.group(2))

            match = OperatorNode.expression.search(tll)
            if match:
                left, right = self._reformSplit(tll, segments, match.span("operator"))
                return OperatorNode(self.constructTree(left), match.group("operator"), self.constructTree(right))

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
                if len(segments) > 1:
                    raise IncorrectLogic(
                        "Found extra tuples of information while matching Concept {}".format(match.group(0))
                    )
                parameters = self._buildParameters(segments[0][1]) if len(segments) else None
                return ConceptNode(match.group(0), callparameters=parameters)

            if tll.strip() in BuiltInFunctionNode.functionList:
                if len(segments) != 1: raise IncorrectLogic("No arguments passed to builtin function {}".format(tll))
                return BuiltInFunctionNode(tll.strip(), self._buildParameters(segments[0][1]))
            
            raise IncorrectLogic("Could not match logic with any node type: '{}'".format(tll))
        except IncorrectLogic as e:
            raise IncorrectLogic("Could not parse sub logic for '{}'".format(logic)) from e

    def _buildParameters(self, logic: str) -> [EvalTree]:
        """ Convert a logic string that represents a tuple of arguments into a list of Evaltrees for each element in 
        the same original order. These shall form the parameters of a EvalTree node in the logic.

        Params:
            logic (str): A tuple of arguments to be converted e.g. (%.age, 12, something)

        Returns:
            [EvalTree]: A collection of EvalTrees that represent the logic
        """
        logic = logic[1:-1]
        logic = logic.split(",")
        if logic == [""]: return []
        else: return [self.constructTree(param) for param in logic]

    @staticmethod
    def _breakdown_logic(logic: str) -> (str, [(int, str)]):
        """ Identify that parts of the logic that can be considered "top level" and remove the sub-level logic recording
        their original position within the logic. This breaks down the logic provided such that the hiearchy of EvalTree
        Nodes can be established

        Params:
            logic (str): A human readable logical string

        Returns:
            str: A string of the top level, most relevent, logic to be processed first
            [(int, str)]: Segments of the original logic string that have been removed, index of their original location
                and their value
        """

        # The currently openned parenthesis index + the number of inner open parenthesis before its close
        indexOfOpenned, ignoreCount = None, 0  
        segments = []

        parenthesisError = IncorrectLogic("Parenthesis miss match while examining logic: {}".format(logic))

        for i, char in enumerate(logic):
            if char is "(":
                if indexOfOpenned is None: indexOfOpenned = i  # Found a new segment, record index
                else: ignoreCount += 1  # Found open parethesis between open and close

            if char is ")":
                if indexOfOpenned is None: raise parenthesisError

                if ignoreCount: ignoreCount -= 1  # Closed a inbetween segment
                else:
                    # Segment complete, record segment and remove reference to open parenthesis
                    segments.append((indexOfOpenned, i))
                    indexOfOpenned = None

        if indexOfOpenned: raise parenthesisError

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
    def _reformSplit(logic: str, segments: [(int, str)], split_span: (int, int)) -> (str, str):
        """ Reform a broken down piece of logic by inserting the extracted segments back into their rightful place.
        The reformed string is then split according to a span object, the span is in relation to the top level logic
        view, and is according to an expression of one of the Eval tree nodes.

        Params:
            logic (str): The top level logic
            segments ([(int, str)]): Segments of logic to be returned to their respective index
            split_span (int, int): The span of the intended split. The span content is lost.

        Returns:
            str: logic to the left of the split
            str: logic to the right og the split
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