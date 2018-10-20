import re

from ..evaltrees import EvalTree
from .relationnode import RelationNode

from ...exceptions import IncorrectLogic

class BuiltInFunctionNode(EvalTree):
    # TODO: Documentation

    functionList = [
        "graph",
        "facts",
        "is",
        "isNot"
    ]

    def __init__(self, function_name: str, parameters: [EvalTree]):

        self.__function_list = {
            "graph": self.graph,
            "facts": self.facts,
            "is": self.isFunc,
            "isNot": self.isNot
        }

        self.function = function_name
        self.function_parameters = parameters

    def __str__(self):
        return self.function + "({})".format(",".join([str(x) for x in self.function_parameters]))

    def parameters(self):
        return [param for func_param in self.function_parameters for param in func_param.parameters()]

    def eval(self, **kwargs):
        try:
            return self.__function_list[self.function](*self.function_parameters, **kwargs)
        except Exception as e:
            import sys
            raise IncorrectLogic("Logical error for : {} - Context: {}".format(self, e)).with_traceback(sys.exc_info()[2])

    @staticmethod
    def graph(*args, **kwargs):
        # TODO: Builtin graph function documentation

        assert(len(args) > 0)
        args = [node.eval(**kwargs) for node in args]

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

    @staticmethod
    def facts(relation_node: EvalTree, **kwargs) -> float:
        """ Calculate the value for a relation using only the rules within any conditions. Calculate
        this value and return it
        
        Params:
            relation_node (RelationNode): Relation container

        Returns:
            float: The confidence of the relation on based on conditionless rules only
        """

        if not isinstance(relation_node, RelationNode):
            raise IncorrectLogic("Built in function facts received something other than a relation - {}".format(relation_node))

        kwargs["evaluate_conditions"] = True
        return relation_node.eval(**kwargs)

    @staticmethod
    def isFunc(concept_one: EvalTree, concept_two, **kwargs) -> float:
        """ Test to determine if any two instances are the same - As the language is defined, it 
        would be possible to ensure this for named concepts, however, the domain and target are 
        special.

        Intended to be used to determine if a named concept is the same instance as one of the 
        domain and instance concepts. Can be used to differ two different named concepts of the same
        concept however - but likely shouldn't...

        Returns:
            float - 100.0 if true else 0.0

        >>> is(%, #example)
        100
        >>> is(#[1]example, #[another_tag]example)
        0

        Params:
            concept_one (EvalTree::ConceptNode) - A concept node
            concept_two (EvalTree::ConceptNode) - A concept node
        """
        return (concept_one.instance(**kwargs) is concept_two.instance(**kwargs))*100

    @staticmethod
    def isNot(concept_one: EvalTree, concept_two, **kwargs) -> float:
        """ The opposite of the is built in function - Test whether two instances are not the same.
        This would be useful when two named concepts are involved, the scenario implied that they 
        shouldn't be linked, but they can be.

        Returns
            float - 100.0 if true else 0.0

        >>> isNot(#[0]example, #[1]example)
        0
        >>> isNot(#[0]example, @)
        100
        """
        return (concept_one.instance(**kwargs) is not concept_two.instance(**kwargs))*100

    @staticmethod
    def approx(value, target, degrees_of_freedom) -> float:
        """ Check if a value is close to another with a given indicator of degrees of freedom """
        
        #TODO implement this cool function bro - approx in builtins
        pass