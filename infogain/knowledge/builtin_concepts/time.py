from ..instance import ConceptInstance

class Date(ConceptInstance):
    """ A concept that represents a specific date """

    def __init__(self):

        from ..concept import Concept
        date = Concept("Date")

        ConceptInstance.__init__(self, date)
    


class Time(ConceptInstance):
    pass

class Datetime(Date, Time):

    pass

class Period(ConceptInstance):





    pass