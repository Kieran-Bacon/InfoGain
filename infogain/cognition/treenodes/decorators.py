from ...exceptions import IncorrectLogic, ConsistencyError

def scenario_consistent(function):
    """ Ensure that a scenario has been passed to the function """

    def wrapper(self, *args, **kwargs):

        if "scenario" not in kwargs:
            raise ConsistencyError("No Scenario was passed through the evaluation tree for {} - {}".format(type(self), self))

        if hasattr(self, "__scenario_requires__"):

            missing = set(self.__scenario_requires__).difference(set(kwargs["scenario"].keys()))

            if missing:
                raise ConsistencyError("Scenario is missing required entry for {} {}: missing: {}".format(type(self), self, missing))                    

        return function(self, *args, **kwargs)

    return wrapper