import json

from .Ontology import Ontology
from .RelationExtractor import Datapoint

class Document():
    """ Representation of processable documents. """

    def __init__(self, ontology: Ontology):
        pass

    def sentenceEmbed(sentence: str) -> [int]:
        """ Convert the sentence into a vector """
        return [len(sentence)]*300

class TrainingDocument(Document):

    def __init__(self, ontology: Ontology, content = None, file_address = None):
        self.ontology = ontology # Storage a reference to the ontology
        self.datapoints = set()

        if not file_address is None:
            with open(file_address) as filehandler:
                content = json.load(filehandler)

        for data in content["datapoints"]:
            # Assign text representations to the concepts
            self.ontology.concept(data["domain"]["concept"]).addRepr(data["domain"]["text"])
            self.ontology.concept(data["target"]["concept"]).addRepr(data["target"]["text"])

            self.datapoints.add(Datapoint(\
                data["domain"]["concept"],\
                data["target"]["concept"],\
                data["relation"],\
                Document.sentenceEmbed(data["lContext"]),\
                Document.sentenceEmbed(data["mContext"]),\
                Document.sentenceEmbed(data["rContext"]),\
                data["class"]))