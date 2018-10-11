from inspect import signature

from ..information import Vertice, Edge

class Instance(Vertice):
    """ An instance of a concept. The concept an instance represents is responsible for 
    generating its instance - the responsiblity of ensuring correctness within the instance is
    therefore handled by the concept. 

    No abstract concept will have a instance

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

    def __getattr__(self, attribute):
        return self._properties.get(attribute)

    def __str__(self):
        return self.name