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
        self.concept = concept_name
        self.name = instance_name if instance_name is not None else self.concept
        self.properties = properties  # Data structure to contain the properties of the instance

    def __str__(self): return self.name
    def __hash__(self):
        if "__self__" in self.properties: return hash(self.properties["__self__"])
        else: return Vertice.__hash__(self)
    def __eq__(self, other):
        if "__self__" in self.properties: return self.properties["__self__"] == other
        else: return Vertice.__eq__(self, other)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    def __getattr__(self, attribute): return self.properties.get(attribute)
    def __getitem__(self, attribute): return self.properties.get(attribute)
    def __call__(self, *args, **kwargs): return self.__class__(*args, **kwargs)