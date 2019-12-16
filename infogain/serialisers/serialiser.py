from abc import abstractmethod

from ..artefact.document import Document
from ..knowledge.ontology import Ontology

class AbstractSerialiser:

    def __init__(self, classtype: Ontology = Ontology):
        # The class
        self._classtype = classtype
        self._writeMethod = "w"

    @abstractmethod
    def load(self, filepath: str):
        """ Load the contents of the file at the location provided with via the
        encoding method implemented

        Params:
        """
        raise NotImplementedError()

    @abstractmethod
    def dump(self, ontology: Ontology) -> object:
        """ Convert the provided ontology into an python object that represents the serialised version of the ontology

        Params:
            ontology (Ontology): The ontology to be serialised
        """
        raise NotImplementedError()

    def save(self, ontology: Ontology,  filepath: str):
        """ Save the contents of an ontology to a file at the location passed
        with the encoding of the instance

        Params:
            ontology (Ontology): The ontology object to be serialised into
            filepath (str): The path to where the serialised knowledge is to be placed
        """
        with open(filepath, self._writeMethod) as handler:
            handler.write(self.dump(ontology))

_SERIALENCODERS = {}
_DOCUMENTENCODERS = {}
def registerSerialiser(encoder_name: str, _type: object = "ontology"):
    """ Register a Serialiser object against its name such that

    Params:
        encoder_name (str): The name of the encoder, to identify the desired serialiser when saving
    """

    def store_encoder(encoder: object):
        if _type == "ontology":
            _SERIALENCODERS[encoder_name] = encoder
        else:
            _DOCUMENTENCODERS[encoder_name] = encoder

    return store_encoder


class SerialiserFactory(AbstractSerialiser):
    """ Generate a new Serialiser object for the encoding type that has been
    provided to load/save infogain components

    Params:
        encoding (str): A string indicating the encoding type/format for
            the knowledge
        classtype (Ontology): Ontology class that is to be serialised into
            and from
    """

    def __new__(cls, encoding: str = "python", classtype: Ontology = Ontology):
        """ Generate a new Serialiser object for the encoding type that has been
        provided to load/save infogain components

        Params:
            encoding (str): A string indicating the encoding type/format for
                the knowledge
            classtype (Ontology): Ontology class that is to be serialised into
                and from

        Raise:
            KeyError: when an encoder is specified that doesn't exist for the classtype given
            TypeError: when the classtype given is not recognised
        """

        if issubclass(classtype, Ontology):
            return _SERIALENCODERS[encoding](classtype)
        elif issubclass(classtype, Document):
            return _DOCUMENTENCODERS[encoding](classtype)
        else:
            raise TypeError("Unrecognised class type provided '{}'".format(str(classtype)))

    def __init__(self, encoding: str = "python", classtype: Ontology = Ontology):
        pass