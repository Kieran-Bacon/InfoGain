import re, math, itertools

from ..evaltrees import EvalTree
from .conceptnode import ConceptNode
from .relationnode import RelationNode
from .numbernode import NumberNode

from ...exceptions import IncorrectLogic, ConsistencyError
from .decorators import scenario_consistent


import logging
log = logging.getLogger(__name__)

class BuiltInFunctionNode(EvalTree):
    """ This node handles builtin functions and their behaviour. Built in functions can be called from anywhere within
    the logic and are meant to expose the functionality that is in high demand.

    Params:
        function_name (str): The name of the function
        parameters ([EvalTree]): The parameters that is being passed into the builtin
    """

    functionList = [
        "count",
        "f",
        "facts",
        "is",
        "isNot",
        "approx",
        "eq",
        "eqNot"
    ]

    def __init__(self, function_name: str, parameters: [EvalTree]):

        self.function_name = function_name
        self.function_parameters = parameters

        if function_name == "count":
            # For the concept
            if parameters is []:
                raise IncorrectLogic("Builtin function 'count' requies at least 1 parameter - None given")

            # Extract the parameters
            target, filters = parameters[0], parameters[1:]

            if isinstance(target, ConceptNode):
                targetParameters = target.parameters()

                for f in filters:
                    if targetParameters != f.parameters():
                        raise IncorrectLogic("Builtin function 'count' defined incorrectly " +
                                             "- filter {} doesn't reference target {}".format(f, target))

            elif isinstance(target, RelationNode):

                targetParameters = target.parameters()

                for f in filters:
                    filter_parameters = f.parameters()

                    if not targetParameters.intersection(filter_parameters):
                        # The filter parameters contain either other concepts or no parameters
                        raise IncorrectLogic("Builtin function 'count' defined incorrectly - "+
                                             "filter {} doesn't reference either target {}".format(f, targetParameters))
            else:
                raise IncorrectLogic("Builtin function count passed invalid target node: "+
                                     "{} - Excepts Concepts or Relations only".format(type(target)))

            self.function = self.count

        elif function_name == "f": self.function = self.f
        elif function_name == "facts":

            if len(self.function_parameters) != 1:
                raise IncorrectLogic("Builtin function 'fact' takes only 1 argument - {} provided".format(
                    len(self.function_parameters)))

            if not isinstance(self.function_parameters[0], RelationNode):
                raise IncorrectLogic("Builtin function 'fact' requires Relation - {} provided".format(
                    type(self.function_parameters[0])
                ))

            self.function = self.facts
        elif function_name == "is": self.function = self.isFunc
        elif function_name == "isNot": self.function = self.isNot
        elif function_name == "approx": self.function = self.approx
        elif function_name == "eq": self.function = self.eq
        elif function_name == "eqNot": self.function = self.eqNot
        else: raise IncorrectLogic("Builtin function name not recognised {}".format(self.function_name))

    def __str__(self): return self.function_name + "({})".format(",".join([str(x) for x in self.function_parameters]))
    def parameters(self):
        if self.function_name in ["count"]: return set()
        return {param for params in self.function_parameters for param in params.parameters()}

    def eval(self, **kwargs):
        try:
            return self.function(*self.function_parameters, **kwargs)
        except Exception as e:
            raise RuntimeError("Invalid logic evaluation for {}".format(self)) from e

    @staticmethod
    def count(*args, **kwargs):
        """ Count the number of instances/relationships given various criteria

        >>>count(#Person, #Person.age > 10)
        10
        >>>count(#Person=attends=#Class, #Person.age > 24, #Person.sex == 'M')
        2

        con1: %=friendswith=#Person
        con2: count(#Person=visited=#Country, #Country.size > 10000)

        Person and person overlay so they connect.
        """
        engine = kwargs["engine"]

        countTarget = args[0]  # The expression that needs to be counted
        filters = args[1:]  # The filter expressions

        def apply_filters(collection: [dict]):

            # Apply the filters in order removing instances that do not pass
            temp = []
            for f in filters:
                for inst in collection:
                    evaluation = f.eval(**{**kwargs, **inst})

                    if not isinstance(evaluation, bool):
                        log.warning("count filter didn't evaluate to a bool {}".format(f))

                    if evaluation: temp.append(inst)

                collection = temp
                temp = []

            return collection


        if isinstance(countTarget, ConceptNode):

            # Extract the concept and its representation in the logic
            parameter = countTarget.parameters().pop()
            concept = EvalTree.paramToConcept(parameter)

            # Collect together all the instances for the concept
            collection = [{"scenario": {parameter: inst}} for inst in engine.instances(*concept)]
            collection = apply_filters(collection)

            # Return the length of the remain collection
            return len(collection)

        elif isinstance(countTarget, RelationNode):

            # From the relationship, get the domain concept name and information as to whether it should be expanded
            domainParam = countTarget.domain.parameters().pop()
            if EvalTree.isPlaceholder(domainParam): domain = (countTarget.domain.instance(**kwargs).concept, False)
            else: domain = EvalTree.paramToConcept(domainParam)

            # From the relationship, get the target concept name and information as to whether it should be expanded
            targetParam = countTarget.target.parameters().pop()
            if EvalTree.isPlaceholder(targetParam): target = (countTarget.target.instance(**kwargs).concept, False)
            target = EvalTree.paramToConcept(targetParam)

            # Ensure the relationship is valid for these concepts
            relation = engine.relations[countTarget.relation]
            if not relation.between(engine.concepts[domain[0]], engine.concepts[target[0]]):
                log.warning("Attempting to count relations for invalid concept pairs: {}".format(countTarget))
                return 0

            # Extract the valid instances for this - if the concept is linked via scenario only choose that
            if domainParam in kwargs.get("scenario", []): domInst = {kwargs["scenario"][domainParam]}
            else:                                         domInst = set(engine.instances(*domain))

            if targetParam in kwargs.get("scenario",[]): tarInst = {kwargs["scenario"][targetParam]}
            else:                                        tarInst = set(engine.instances(*target))

            # Filter the instances to those that apply to the relation
            domInst = {dom for dom in domInst if dom.name in relation.domains or dom.concept in relation.domains}
            tarInst = {tar for tar in tarInst if tar.name in relation.targets or tar.concept in relation.targets}

            # No valid instances exist
            if 0 in [len(domInst), len(tarInst)]: return 0

            # Generate the valid scenarios for the instances
            collection = []
            for dom, tar in itertools.product(domInst, tarInst):
                if "scenario" in kwargs:
                    collection.append({"scenario": {**kwargs["scenario"], **{domainParam: dom, targetParam: tar}}})
                else:
                    collection.append({"scenario": {domainParam: dom, targetParam: tar}})

            collection = apply_filters(collection)

            # Evaluate any remaining instances to determine the number of valid instances.
            count = 0
            for inst in collection:
                evaluation = countTarget.eval(**{**kwargs, **inst})
                if evaluation: count += 1

            # Return the length of the remain collection
            return count

    @staticmethod
    def f(*args, **kwargs):
        """ Perform a mathematical function taking arbitary numbers of arguments. Arguments replace
        alphabet characters, function evaluation is returned.

        >>>%.age = 10
        >>>f(12, %.age, x*y)
        120
        """

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
        kwargs["evaluate_conditions"] = False
        return relation_node.eval(**kwargs)

    @staticmethod
    def isFunc(concept_one: EvalTree, concept_two: EvalTree, **kwargs) -> float:
        """ Test to determine if any two instances are the same - As the language is defined, it
        would be possible to ensure this for named concepts, however, the domain and target are
        special.

        Intended to be used to determine if a named concept is the same instance as one of the
        domain and instance concepts. Can be used to differ two different named concepts of the same
        concept however - but likely shouldn't...

        Params:
            concept_one (EvalTree::ConceptNode) - A concept node
            concept_two (EvalTree::ConceptNode) - A concept node

        Returns:
            float - 1. if true else 0.

        >>> is(%, #example)
        100
        >>> is(#[1]example, #[another_tag]example)
        0
        """
        return float(concept_one.instance(**kwargs) is concept_two.instance(**kwargs))

    @staticmethod
    def isNot(concept_one: EvalTree, concept_two, **kwargs) -> float:
        """ The opposite of the is built in function - Test whether two instances are not the same.
        This would be useful when two named concepts are involved, the scenario implied that they
        shouldn't be linked, but they can be.

        Returns
            float - 1. if true else 0.

        >>> isNot(#[0]example, #[1]example)
        0
        >>> isNot(#[0]example, @)
        100
        """
        return float(concept_one.instance(**kwargs) is not concept_two.instance(**kwargs))

    @staticmethod
    def approx(a: EvalTree, b: EvalTree, distance: NumberNode, **kwargs) -> float:
        """ Check if a value is close to another with a given indicator of degrees of freedom """

        a_val, b_val, d_val = a.eval(**kwargs), b.eval(**kwargs), distance.eval(**kwargs)
        prox = math.isclose(a_val, b_val, abs_tol=d_val)

        if prox: return float(1 - (abs(a_val - b_val)/d_val))
        else: return 0.

    @staticmethod
    def eq(a: EvalTree, b: EvalTree, **kwargs): return float(a.eval(**kwargs) == b.eval(**kwargs))
    @staticmethod
    def eqNot(a: EvalTree, b: EvalTree, **kwargs): return float(a.eval(**kwargs) != b.eval(**kwargs))