from inspect import signature

from ..information import Vertice, Edge

class Instance():
    """ Abstract class to imply a instatiation of an ontology object - the base class defines the 
    shared functionality of all instance objects which relate to storing properties of the objects 
    and storing and running of object functions
    """

    def __init__(self):
        self._properties = {}  # A dictionary of properties
        self._functions = {}  # A dictionary of functions with parameters

    def addFunction(self, function: callable):
        """ Add a function to the instance object - to be called using the function method.
        Functions that do not have parameters are also stored as properties for ease of use.

        Params:
            function (callable): The function to be stored against the instance object
        """

        functionSignature = signature(function)  # Extract inspect the signature of the function
        if not functionSignature.parameters: self.addProperty(function.__name__, function)
        
        self._functions[function.__name__] = function  # Save the function to the instance

    def function(self, function_name: str, *args):
        """ Run and return the outcome of the function that has been provided 
        
        Params
            function_name (str): The function identifier, the method name
            *args (objs): Arguments appropriate for the function that is being access

        Returns
            The output of the function - could literally be anything
        """
        if args: return self._functions.get(function_name, self.__empty_function__)(*args)
        else: return self._functions.get(function_name, self.__empty_function__)()

    def removeFunction(self, function_name: str) -> None:
        """ Remove a function from the instance

        Params:
            function_name (str): The name of the function to be removed
        """
        del self._functions[function_name]

    def addProperty(self, prop_name: str, prop_value: object) -> None:
        """ Add a property into the instance 
        
        Params:
            prop_name (str): The property name/identifer
            prop_value (object): The value of the property
        """
        self._properties[prop_name] = prop_value

    def property(self, name: str) -> (object):
        """ Return the value of the property that has been asked for. If the
        property doesn't exist, return None 
        
        Params:
            name (str): The name of the property that is to be returned
        """
        value = self._properties.get(name)  # Extract the object at the location
        return value if not callable(value) else value()  # if the property is a function, run it

    def removeProperty(self, prop_name: str):
        """ Delete the property with the given name 
        
        Params:
            prop_name (str): The property name - identifying the property that is to be deleted
        """
        del self._properties[prop_name]  # Delete reference to the value at the provided key

    @staticmethod
    def __empty_function__(*args):
        """ The empty function method is to be called in the event that a function is missing 

        Params:
            args: The arguments that would have been passed to the target function if it existed
        """
        return None

class ConceptInstance(Instance, Vertice):
    """ An instance of a concept. The concept a ConceptInstance represents is responsible for 
    generating its instance - the responsiblity of ensuring correctness within the instance is
    therefore handled by the concept.

    No abstract concept will have a ConceptInstance

    A static concept will share its internal properties dictionary with this instance - updates to 
    either will have side-effects for the other

    A dynamic concept will have entirely separated properties

    Params:

        concept (knowledge.Concept): The concept this instance resembles
    """

    def __init__(self, concept_name: str, instance_name: str = None, properties: dict = {}):
        Instance.__init__(self)
        self.concept = concept_name
        self.name = instance_name if instance_name is not None else self.concept
        self._properties = properties

    def __str__(self):
        return self.name


class RelationInstance(Instance, Edge):
    """ An instance of a relation paring """
    pass