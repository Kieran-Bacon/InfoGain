from inspect import signature

from ..knowledge import Concept, Relation

class Instance():
    """ Abstract class to imply a instatiation of an ontology object """

    def __init__(self):
        self._properties = {}  # A dictionary of properties
        self._functions = {}  # A dictionary of functions with parameters

    def property(self, name: str) -> (object):
        """ Return the value of the property that has been asked for. If the
        property doesn't exist, return None 
        
        Params:
            name (str): The name of the property that is to be returned
        """
        value = self._properties[name]  # Extract the object at the location
        return value if not callable(value) else value()  # if the property is a function, run it

    def function(self, function_name: str, *args):
        """ Run and return the outcome of the function that has been provided """
        return self._functions.get(function_name, self.__empty_function__)(args)

    def _addProperty(self, prop_name: str, prop_value: object) -> None:
        """ Add a property into the instance """
        self._properties[prop_name] = prop_value

    def _removeProperty(self, prop_name: str):
        """ Delete the property with the given name """
        del self._properties[prop_name]  # Delete reference to the value at the provided key

    def _addFunction(self, function: callable):

        functionSignature = signature(function)  # Extract inspect the signature of the function
        if not functionSignature.parameters: self._addProperty(function.__name__, function)
        
        self._functions[function.__name__] = function  # Save the function to the instance

    @staticmethod
    def __empty_function__(*args):
        return None

class ConceptInstance(Instance, Concept):
    """ A instance of a concept """

    def __init__(self, concept):
        Instance.__init__(self)
        Concept.__init__(self, **concept.minimise())

class RelationInstance(Instance, Relation):
    """ An instance of a relation paring """
    pass