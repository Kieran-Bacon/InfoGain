import re

from ..concept import Concept
from ..instance import Instance

class Email(Instance):
    pass

def concepts():

    email = Concept("EmailAddress")
    email.setInstanceClass(Email)

    return [email]