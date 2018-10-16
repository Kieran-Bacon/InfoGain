from ..concept import Concept
from ..instance import Instance

class Date(Instance): pass
class Time(Instance): pass
class Datetime(Date, Time): pass
class Period(Instance): pass

def concepts():

    date = Concept("Date", children={"Datetime"}, category="static")
    date.setInstanceClass(Date)

    time = Concept("Time", children={"Datetime"}, category="static")
    time.setInstanceClass(Time)

    datetime = Concept("Datetime", parents={"Date", "Time"}, category="static")
    datetime.setInstanceClass(Datetime)

    period = Concept("Period", category="static")
    period.setInstanceClass(Period)

    return [date, time, datetime, period]