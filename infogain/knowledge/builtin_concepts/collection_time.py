import datetime as py_datetime
import time as py_time

from ..concept import Concept
from ..instance import Instance
from ...exceptions import IncorrectLogic

class Date(Instance):

    _self = py_datetime.date  # The class this instances represents

    formats = {
        "%d/%m/%y",
        "%d/%m/%Y",
        "%d-%m-%y",
        "%d-%m-%Y" 
    }

    def __call__(self, date_object: object) -> Instance:
        """ Allow the Date instance to be used to create a new data instance during the processing
        of some logic """

        if isinstance(date_object, str):

            for dateFormat in self.formats:
                try:
                    date = py_datetime.datetime.strptime(date_object, dateFormat).date()
                    break
                except ValueError:
                    # The format was not valid for the string
                    continue
            else:
                raise IncorrectLogic("Attempted to create a date with an invalid string: {}".format(date_object))

            # Create and return the date object
            return Date("Date", str(date), {"__self__": date})

    def before(self, other): return self.properties["__self__"] < other

class Time(Instance):
    _self = py_time
class Datetime(Date, Time):
    _self = py_datetime.datetime
class Period(Instance):
    _self = py_datetime.timedelta

def concepts():

    date = Concept("Date", children={"Datetime"})
    date.setInstanceClass(Date)

    time = Concept("Time", children={"Datetime"})
    time.setInstanceClass(Time)

    datetime = Concept("Datetime", parents={"Date", "Time"})
    datetime.setInstanceClass(Datetime)

    period = Concept("Period")
    period.setInstanceClass(Period)

    return [date, time, datetime, period]