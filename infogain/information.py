class Vertice:
    """ A single point of information """
    def __init__(self):
        self.concept = None
        self.name = None
    def __hash__(self): return hash(self.name)
    def __eq__(self, other):
        if hasattr(self, "concept"):
            # Self is an instance, comparing with a instance, concept and string object
            if hasattr(other, "concept"): return self.concept == other.concept and self.name == other.name
            elif hasattr(other, "name"): return self.concept == other.name
            else: return self.name == other
        else:
            # Self is a concept, compare with instance or (concept/string)
            if hasattr(other, "concept"): return self.name == other.concept
            else: return self.name == other
    def __ne__(self, other): return not self.__eq__(other)