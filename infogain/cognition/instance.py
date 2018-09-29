from inspect import signature

from ..knowledge import Concept, Relation

class Instance():
    """ Abstract class to imply a instatiation of an ontology object - the base class defines the 
    shared functionality of all instance objects which relate to storing properties of the objects 
    and storing and running of object functions
    """

    def __init__(self):
        self._properties = {}  # A dictionary of properties
        self._functions = {}  # A dictionary of functions with parameters

    def property(self, name: str) -> (object):
        """ Return the value of the property that has been asked for. If the
        property doesn't exist, return None 
        
        Params:
            name (str): The name of the property that is to be returned
        """
        value = self._properties.get(name)  # Extract the object at the location
        return value if not callable(value) else value()  # if the property is a function, run it

    def addFunction(self, function: callable):
        """ Add a function to the instance object - to be called using the function method.
        Functions that do not have parameters are also stored as properties for ease of use.

        Params:
            function (callable): The function to be stored against the instance object
        """

        functionSignature = signature(function)  # Extract inspect the signature of the function
        if not functionSignature.parameters: self._addProperty(function.__name__, function)
        
        self._functions[function.__name__] = function  # Save the function to the instance

    def function(self, function_name: str, *args):
        """ Run and return the outcome of the function that has been provided 
        
        Params
            function_name (str): The function identifier, the method name
            *args (objs): Arguments appropriate for the function that is being access

        Returns
            The output of the function - could literally be anything
        """
        print(function_name)
        print(self._functions)
        if args: return self._functions.get(function_name, self.__empty_function__)(*args)
        else: return self._functions.get(function_name, self.__empty_function__)()

    def _addProperty(self, prop_name: str, prop_value: object) -> None:
        """ Add a property into the instance 
        
        Params:
            prop_name (str): The property name/identifer
            prop_value (object): The value of the property
        """
        self._properties[prop_name] = prop_value

    def _removeProperty(self, prop_name: str):
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

class ConceptInstance(Instance, Concept):
    """ A instance of a concept """

    def __init__(self, concept):
        Instance.__init__(self)
        Concept.__init__(self, **concept.minimise())

        self.concept = concept  # Reference back to the original instance
        self._properties = self.properties  # Set the hidden properties dict as a pointer to the concept properties

class RelationInstance(Instance, Relation):
    """ An instance of a relation paring """
    pass