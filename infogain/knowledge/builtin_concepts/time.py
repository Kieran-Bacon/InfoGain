import datetime

from ..concept import Concept
from ..instance import Instance
from ...exceptions import IncorrectLogic

class Date(Instance):

    formats = [
        "%d/%m/%y",
        "%d/%m/%Y",
        "%d-%m-%y",
        "%d-%m-%Y" 
    ]

    def __call__(self, date_object: object) -> Instance:
        """ Allow the Date instance to be used to create a new data instance during the processing
        of some logic """

        if isinstance(date_object, str):

            for dateFormat in self.formats:
                try:
                    date = datetime.datetime.strptime(date_object, dateFormat).date()
                    break
                except ValueError:
                    # The format was not valid for the string
                    continue
            else:
                raise IncorrectLogic("Attempted to create a date with an invalid string: {}".format(date_object))

            # Create and return the date object
            return Date("Date", str(date), {"__self__": date})

    def before(self, other): return self.properties["__self__"] < other




class Time(Instance): pass
class Datetime(Date, Time): pass
class Period(Instance):

    def days(self):
        """ Return the number of days between two """
        pass

    def seconds(self):
        pass

    def length(self, *args):
        """ Find the length of a period of time
        
        >>>a = Period("Period", properties={"period": datetime.timedelta(days=2, seconds=400)})
        >>>a.length()
        (2, 400)

        >>>a.length("18-09-2017", "20-09-2017")
        (2, 0)
        """
        pass

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