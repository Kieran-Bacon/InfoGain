from .serialiser import AbstractSerialiser, registerSerialiser

@registerSerialiser("python")
class PythonSerialiser(AbstractSerialiser):
    """ Serialise the ontology into a valid python object definition of the ontology """
    pass