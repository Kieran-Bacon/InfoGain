class Vertice:
    """ A single point of information """

    def __init__(self):
        self.name = None

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Vertice):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

class Edge:
    """ A connection of two points of information """
    pass