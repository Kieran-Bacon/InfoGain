from ..information import Vertex

class Instance(Vertex):
    """ An instance of a concept. The concept an instance represents is responsible for
    generating its instance - the responsibility of ensuring correctness within the instance is
    therefore handled by the concept.

    No abstract concept will have a instance

    A static concept will share its internal properties dictionary with this instance - updates to
    either will have side-effects for the other

    A dynamic concept will have entirely separated properties

    Params:

        concept (knowledge.Concept): The concept this instance resembles
    """
    _self = None

    def __init__(self, concept_name: str, instance_name: str = None, properties: dict = {}):
        self.concept = concept_name
        self.name = instance_name if instance_name is not None else self.concept
        self.properties = properties  # Data structure to contain the properties of the instance

    def __str__(self): return self.name
    def __repr__(self): return "<Instance of {}: '{}' with properties {}>".format(
        self.concept, self.name, self.properties)
    def __hash__(self):
        if "__self__" in self.properties: return hash(self.properties["__self__"])
        else: return Vertex.__hash__(self)
    def __eq__(self, other):
        if "__self__" in self.properties: return self.properties["__self__"] == other
        else: return Vertex.__eq__(self, other)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    def __getattr__(self, attribute: str) -> object:
        """ In the event that a user has asked for an attribute of an instance that isn't exposed as part of its
        interface, check the internal objects and return the best match that can be found. First check the properties of
        the instance, then the instance this instance maybe representing, finally the class this instance represents.

        Params:
            attribute (str): The attribute name

        Returns:
            object: What ever the attribute type is, or None in the event that it couldn't be found
        """
        try:
            if attribute in self.properties: return self.properties[attribute]
            elif "__self__" in self.properties: return getattr(self.properties["__self__"], attribute)
            elif self._self is not None: return getattr(self._self, attribute)
            else: return None
        except AttributeError:
            return None

    def __getitem__(self, attribute): return self.properties.get(attribute)
    def __call__(self, *args, **kwargs): return self.__class__(*args, **kwargs)